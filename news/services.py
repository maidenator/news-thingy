from datetime import datetime, timezone as dt_timezone
from email.utils import parsedate_to_datetime
import html
import re
import urllib.request
import xml.etree.ElementTree as ET

from django.utils import timezone

from news.models import Article, Outlet, Summary

DEFAULT_RSS_FEEDS = {
    'rappler': 'https://www.rappler.com/feed/',
    'inquirer': 'https://newsinfo.inquirer.net/feed',
    'businessworld': 'https://www.bworldonline.com/feed/',
    'gma-news': 'https://data.gmanetwork.com/gno/rss/news/feed.xml',
    'philstar': 'https://www.philstar.com/rss/headlines',
    'abs-cbn': 'https://news.google.com/rss/search?q=site:abs-cbn.com+Philippines&hl=en-PH&gl=PH&ceid=PH:en',
}

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) NewsThingy/1.0'
TAG_RE = re.compile(r'<[^>]+>')
SPACE_RE = re.compile(r'\s+')
SENTENCE_SPLIT_RE = re.compile(r'(?<=[.!?])\s+')
IMG_SRC_RE = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)
META_TAG_RE = re.compile(r'<meta\s+[^>]*>', re.IGNORECASE)
ATTR_RE = re.compile(r'([a-zA-Z0-9_:-]+)\s*=\s*["\']([^"\']*)["\']')
MEDIA_NS = '{http://search.yahoo.com/mrss/}'
CONTENT_NS = '{http://purl.org/rss/1.0/modules/content/}'


def _normalize_image_url(url):
    if not url:
        return ''
    cleaned = html.unescape(url.strip())
    if cleaned.startswith('//'):
        cleaned = 'https:' + cleaned
    if cleaned.startswith(('http://', 'https://')) and len(cleaned) <= 500:
        return cleaned
    return ''


def extract_image_from_html_fragment(raw_html):
    """Extract the first valid image src URL from an HTML snippet."""
    if not raw_html:
        return ''
    match = IMG_SRC_RE.search(html.unescape(raw_html))
    return _normalize_image_url(match.group(1)) if match else ''


def extract_og_image_from_html(page_html):
    """Extract og:image or twitter:image URL from an article's HTML head."""
    if not page_html:
        return ''
    head_slice = page_html[:40000]
    for tag in META_TAG_RE.findall(head_slice):
        attrs = {k.lower(): v for k, v in ATTR_RE.findall(tag)}
        key = (attrs.get('property') or attrs.get('name') or '').lower()
        if key in ('og:image', 'og:image:secure_url', 'twitter:image', 'twitter:image:src'):
            candidate = _normalize_image_url(attrs.get('content', ''))
            if candidate:
                return candidate
    return ''


def fetch_article_og_image(url, timeout=6, fetcher=None):
    """Fetch an article webpage and extract its og:image / twitter:image thumbnail."""
    if not url or not url.startswith(('http://', 'https://')):
        return ''
    fetch_fn = fetcher or _default_url_fetcher
    try:
        raw = fetch_fn(url, timeout=timeout)
        page_html = raw.decode('utf-8', errors='ignore') if isinstance(raw, bytes) else str(raw)
        return extract_og_image_from_html(page_html)
    except Exception:
        return ''


def clean_html_text(raw_text):
    """Strip HTML tags, unescape entities, and normalize whitespace."""
    if not raw_text:
        return ''
    unescaped = html.unescape(raw_text)
    stripped = TAG_RE.sub(' ', unescaped)
    return SPACE_RE.sub(' ', stripped).strip()


def parse_rss_date(raw_date):
    """Parse RFC-2822 or ISO-8601 pubDate strings into a timezone-aware datetime."""
    if not raw_date:
        return timezone.now()
    text = raw_date.strip()
    try:
        dt = parsedate_to_datetime(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=dt_timezone.utc)
        return dt
    except (TypeError, ValueError):
        pass
    try:
        dt = datetime.fromisoformat(text.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=dt_timezone.utc)
        return dt
    except ValueError:
        return timezone.now()


def _extract_rss_item_image(item):
    """Extract thumbnail URL from RSS media tags, enclosures, or inline HTML."""
    for tag_name in (f'{MEDIA_NS}content', f'{MEDIA_NS}thumbnail', 'enclosure'):
        for el in item.findall(tag_name):
            url = el.attrib.get('url', '')
            media_type = (el.attrib.get('type') or '').lower()
            medium = (el.attrib.get('medium') or '').lower()
            if tag_name == 'enclosure' and media_type and not media_type.startswith('image/'):
                continue
            if medium and medium != 'image':
                continue
            normalized = _normalize_image_url(url)
            if normalized:
                return normalized
    for html_field in (item.findtext(f'{CONTENT_NS}encoded'), item.findtext('description')):
        candidate = extract_image_from_html_fragment(html_field)
        if candidate:
            return candidate
    return ''


def parse_rss_xml(xml_bytes, limit=5):
    """Parse RSS 2.0 or Atom XML bytes into normalized article dictionaries."""
    root = ET.fromstring(xml_bytes)
    items = []

    rss_items = root.findall('.//item')
    if rss_items:
        for item in rss_items:
            title = clean_html_text(item.findtext('title'))
            link = (item.findtext('link') or '').strip()
            description = clean_html_text(item.findtext('description'))
            pub_date = item.findtext('pubDate')
            author = clean_html_text(
                item.findtext('{http://purl.org/dc/elements/1.1/}creator')
                or item.findtext('author')
            )
            image_url = _extract_rss_item_image(item)
            if not title or not link or len(link) > 200:
                continue
            items.append({
                'title': title[:300],
                'url': link,
                'image_url': image_url,
                'description': description,
                'author': (author or 'Editorial Desk')[:150],
                'published_at': parse_rss_date(pub_date),
            })
            if len(items) >= limit:
                break
        return items

    # Atom fallback
    atom_ns = '{http://www.w3.org/2005/Atom}'
    for entry in root.findall(f'.//{atom_ns}entry'):
        title = clean_html_text(entry.findtext(f'{atom_ns}title'))
        link_el = entry.find(f'{atom_ns}link')
        link = (link_el.attrib.get('href', '') if link_el is not None else '').strip()
        raw_summary = entry.findtext(f'{atom_ns}summary') or entry.findtext(f'{atom_ns}content')
        summary = clean_html_text(raw_summary)
        updated = entry.findtext(f'{atom_ns}updated') or entry.findtext(f'{atom_ns}published')
        author = clean_html_text(entry.findtext(f'{atom_ns}author/{atom_ns}name'))
        image_url = _extract_rss_item_image(entry) or extract_image_from_html_fragment(raw_summary)
        if not title or not link or len(link) > 200:
            continue
        items.append({
            'title': title[:300],
            'url': link,
            'image_url': image_url,
            'description': summary,
            'author': (author or 'Editorial Desk')[:150],
            'published_at': parse_rss_date(updated),
        })
        if len(items) >= limit:
            break

    return items


def build_summary_fields(title, description):
    """Build a concise TL;DR and key takeaways from RSS headline and excerpt."""
    sentences = [s.strip() for s in SENTENCE_SPLIT_RE.split(description or '') if len(s.strip()) >= 20]
    if sentences:
        tldr = ' '.join(sentences[:2])[:500]
        takeaways = [s[:220] for s in sentences[:3]]
    else:
        tldr = f"{title}. Read the original publisher dispatch for complete reporting."
        takeaways = [title[:220]]

    word_count = len((description or title).split())
    original_read_minutes = max(3, min(10, round(word_count / 30) + 3))
    summary_read_seconds = max(25, min(60, round(len(tldr.split()) / 3)))
    return {
        'tldr': tldr,
        'key_takeaways': takeaways,
        'original_read_time_minutes': original_read_minutes,
        'summary_read_time_seconds': summary_read_seconds,
        'ai_model': 'RSS Extractive Digest',
    }


def _default_url_fetcher(url, timeout=10):
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def fetch_outlet_articles(outlet, limit=3, timeout=10, fetcher=None):
    """Fetch and store latest RSS articles for a single Outlet."""
    feed_url = (outlet.rss_feed_url or '').strip()
    if not feed_url and outlet.slug in DEFAULT_RSS_FEEDS:
        feed_url = DEFAULT_RSS_FEEDS[outlet.slug]
        outlet.rss_feed_url = feed_url
        outlet.save(update_fields=['rss_feed_url'])

    if not feed_url:
        return 0, f'{outlet.name}: no RSS feed URL configured.'

    fetch_fn = fetcher or _default_url_fetcher
    try:
        xml_bytes = fetch_fn(feed_url, timeout=timeout)
        parsed_items = parse_rss_xml(xml_bytes, limit=limit)
    except Exception as exc:
        return 0, f'{outlet.name}: {exc}'

    created_count = 0
    for item in parsed_items:
        image_url = item.get('image_url', '')
        if not image_url and fetcher is None:
            image_url = fetch_article_og_image(item['url'], timeout=min(timeout, 6))
        summary_data = build_summary_fields(item['title'], item['description'])
        article, created = Article.objects.get_or_create(
            url=item['url'],
            defaults={
                'outlet': outlet,
                'category': outlet.category,
                'title': item['title'],
                'image_url': image_url,
                'author': item['author'],
                'published_at': item['published_at'],
                'original_read_time_minutes': summary_data['original_read_time_minutes'],
            },
        )
        if not created and image_url and not article.image_url:
            article.image_url = image_url
            article.save(update_fields=['image_url'])
        if created:
            Summary.objects.create(
                article=article,
                tldr=summary_data['tldr'],
                key_takeaways=summary_data['key_takeaways'],
                summary_read_time_seconds=summary_data['summary_read_time_seconds'],
                ai_model=summary_data['ai_model'],
            )
            created_count += 1

    return created_count, None


def backfill_missing_thumbnails(limit=30, timeout=6):
    """Fetch og:image thumbnails directly from article pages for articles missing image_url."""
    updated = 0
    for article in Article.objects.filter(image_url='')[:limit]:
        img = fetch_article_og_image(article.url, timeout=timeout)
        if img:
            article.image_url = img
            article.save(update_fields=['image_url'])
            updated += 1
    return updated


def fetch_all_outlets(limit_per_outlet=3, outlet_slug=None, timeout=10, fetcher=None):
    """Fetch latest RSS articles across all (or one specified) configured outlets."""
    outlets = Outlet.objects.select_related('category').all()
    if outlet_slug:
        outlets = outlets.filter(slug=outlet_slug)

    total_created = 0
    checked = 0
    errors = []
    for outlet in outlets:
        checked += 1
        created, error = fetch_outlet_articles(
            outlet,
            limit=limit_per_outlet,
            timeout=timeout,
            fetcher=fetcher,
        )
        total_created += created
        if error:
            errors.append(error)

    return {
        'created': total_created,
        'checked': checked,
        'errors': errors,
    }
