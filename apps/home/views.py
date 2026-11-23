from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from news.models import Article, Category, Outlet, UserSubscription
from news.services import fetch_all_outlets

PROMO_CUES = (
    'gear up for',
    'sponsored',
    'advertorial',
    'partner content',
    'promo',
    'sale',
    'giveaway',
    'team up to power',
)


def _score_article(article, subscribed_outlet_ids, now):
    """Rank stories by editorial depth, visual richness, reader signals, and freshness."""
    score = 0
    has_summary = hasattr(article, 'summary') and article.summary is not None
    takeaway_count = len(article.summary.key_takeaways) if has_summary and article.summary.key_takeaways else 0
    bookmarks = getattr(article, 'bookmark_count', 0) or 0
    reads = getattr(article, 'read_count', 0) or 0

    if has_summary:
        score += 15
        score += min(takeaway_count, 3) * 4
    if article.original_read_time_minutes >= 6:
        score += 8
    elif article.original_read_time_minutes >= 4:
        score += 4

    if article.image_url:
        score += 15

    score += min(bookmarks * 6, 18)
    score += min(reads * 2, 8)

    if article.outlet_id in subscribed_outlet_ids:
        score += 10

    age_hours = max(0.0, (now - article.published_at).total_seconds() / 3600.0)
    if age_hours <= 12:
        score += 20
    elif age_hours <= 24:
        score += 15
    elif age_hours <= 72:
        score += 10
    else:
        score += 4

    title_lower = (article.title or '').lower()
    if any(cue in title_lower for cue in PROMO_CUES):
        score -= 30

    if bookmarks >= 1:
        reason = 'Reader Pick'
    elif takeaway_count >= 3 and article.original_read_time_minutes >= 6:
        reason = 'In-Depth Briefing'
    elif article.outlet_id in subscribed_outlet_ids:
        reason = 'From Your Sources'
    else:
        reason = 'Top Dispatch'

    return score, reason


def _redirect_back(request, fallback):
    """Redirect to a safe HTTP_REFERER when present, otherwise to fallback."""
    referer = request.META.get('HTTP_REFERER')
    if referer and url_has_allowed_host_and_scheme(
        referer,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(referer)
    return redirect(fallback)


def _toggle_user_relation(relation, user):
    """Toggle user membership on a ManyToMany relation; return True if added."""
    if relation.filter(id=user.id).exists():
        relation.remove(user)
        return False
    relation.add(user)
    return True


@login_required
def home_view(request):
    subscription, _ = UserSubscription.objects.get_or_create(user=request.user)
    active_category = request.GET.get('category', 'all')
    search_query = request.GET.get('q', '').strip()
    saved_only = request.GET.get('saved') == '1'
    following_only = request.GET.get('following') == '1'
    unread_only = request.GET.get('unread') == '1'
    subscribed_outlet_ids = set(subscription.outlets.values_list('id', flat=True))

    articles_qs = (
        Article.objects
        .select_related('outlet', 'category', 'summary')
        .annotate(
            bookmark_count=Count('bookmarked_by', distinct=True),
            read_count=Count('read_by', distinct=True),
        )
        .order_by('-published_at')
    )
    if active_category != 'all':
        articles_qs = articles_qs.filter(category__slug=active_category)
    if saved_only:
        articles_qs = articles_qs.filter(bookmarked_by=request.user)
    if following_only:
        articles_qs = articles_qs.filter(outlet_id__in=subscribed_outlet_ids)
    if unread_only:
        articles_qs = articles_qs.exclude(read_by=request.user)
    if search_query:
        articles_qs = articles_qs.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(outlet__name__icontains=search_query) |
            Q(summary__tldr__icontains=search_query)
        )

    chronological_articles = list(articles_qs)
    now = timezone.now()
    for article in chronological_articles:
        score, reason = _score_article(article, subscribed_outlet_ids, now)
        article.editorial_score = score
        article.editorial_reason = reason

    ranked_articles = sorted(
        chronological_articles,
        key=lambda a: (a.editorial_score, a.published_at),
        reverse=True,
    )
    lead_story = ranked_articles[0] if ranked_articles else None
    featured_stories = ranked_articles[1:5]
    more_stories = ranked_articles[5:]
    latest_happenings = chronological_articles[:8]

    user_bookmarked_ids = set(request.user.bookmarked_articles.values_list('id', flat=True))
    user_read_ids = set(request.user.read_articles.values_list('id', flat=True))
    saved_count = len(user_bookmarked_ids)
    unread_count = Article.objects.exclude(read_by=request.user).count()
    is_filtered = bool(
        search_query or active_category != 'all' or saved_only or following_only or unread_only
    )

    return render(request, 'home/home.html', {
        'subscription': subscription,
        'subscribed_outlet_ids': subscribed_outlet_ids,
        'user_bookmarked_ids': user_bookmarked_ids,
        'user_read_ids': user_read_ids,
        'saved_count': saved_count,
        'unread_count': unread_count,
        'saved_only': saved_only,
        'following_only': following_only,
        'unread_only': unread_only,
        'is_filtered': is_filtered,
        'categories': Category.objects.all(),
        'outlets': Outlet.objects.all(),
        'articles': ranked_articles,
        'lead_story': lead_story,
        'featured_stories': featured_stories,
        'more_stories': more_stories,
        'latest_happenings': latest_happenings,
        'active_category': active_category,
        'search_query': search_query,
        'total_articles_count': len(ranked_articles),
        'total_minutes_saved': sum(a.summary.minutes_saved for a in ranked_articles if hasattr(a, 'summary')),
        'user_outlets_count': len(subscribed_outlet_ids),
    })


@login_required
def article_detail_view(request, article_id):
    article = get_object_or_404(
        Article.objects.select_related('outlet', 'category', 'summary'),
        id=article_id,
    )
    is_bookmarked = article.bookmarked_by.filter(id=request.user.id).exists()
    is_read = article.read_by.filter(id=request.user.id).exists()
    related_articles = list(
        Article.objects.select_related('outlet', 'category', 'summary')
        .filter(category=article.category)
        .exclude(id=article.id)[:3]
    )
    return render(request, 'home/article_detail.html', {
        'article': article,
        'is_bookmarked': is_bookmarked,
        'is_read': is_read,
        'related_articles': related_articles,
    })


@login_required
def toggle_read_view(request, article_id):
    if request.method == 'POST':
        article = get_object_or_404(Article, id=article_id)
        if _toggle_user_relation(article.read_by, request.user):
            messages.success(request, f'Marked "{article.title}" as read.')
        else:
            messages.info(request, f'Marked "{article.title}" as unread.')
    return _redirect_back(request, 'home:home')


@login_required
def toggle_bookmark_view(request, article_id):
    if request.method == 'POST':
        article = get_object_or_404(Article, id=article_id)
        if _toggle_user_relation(article.bookmarked_by, request.user):
            messages.success(request, f'Saved "{article.title}" to your bookmarks.')
        else:
            messages.info(request, f'Removed "{article.title}" from your bookmarks.')
    return _redirect_back(request, 'home:home')


@login_required
def fetch_latest_news_view(request):
    if request.method == 'POST':
        result = fetch_all_outlets(limit_per_outlet=2, timeout=8)
        if result['created'] > 0:
            messages.success(
                request,
                f"Fetched {result['created']} new stor{'y' if result['created'] == 1 else 'ies'} from {result['checked']} newsroom(s).",
            )
        elif result['errors'] and result['checked'] == len(result['errors']):
            messages.warning(request, 'Could not reach RSS feeds right now. Showing saved articles.')
        else:
            messages.info(request, 'Your briefing is already up to date with the latest RSS dispatches.')
    return _redirect_back(request, 'home:home')


@login_required
def toggle_subscription_view(request, outlet_id):
    if request.method == 'POST':
        outlet = get_object_or_404(Outlet, id=outlet_id)
        subscription, _ = UserSubscription.objects.get_or_create(user=request.user)
        if subscription.outlets.filter(id=outlet.id).exists():
            subscription.outlets.remove(outlet)
            messages.info(request, f'Unfollowed {outlet.name}.')
        else:
            subscription.outlets.add(outlet)
            messages.success(request, f'Now following {outlet.name}.')
    return _redirect_back(request, 'home:home')
