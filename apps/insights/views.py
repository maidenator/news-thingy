from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Subquery
from django.shortcuts import render
import sqlparse

from news.models import Article, Category, Outlet, Summary


def _format_sql(queryset):
    return sqlparse.format(str(queryset.query), reindent=True, keyword_case='upper')


def _attach_breakdown_percentages(items):
    """Attach relative article share and summary coverage percentages for UI bars."""
    max_articles = max((item.article_count for item in items), default=1) or 1
    for item in items:
        item.share_pct = round((item.article_count / max_articles) * 100)
        item.coverage_pct = (
            round((item.summary_count / item.article_count) * 100)
            if item.article_count
            else 0
        )
    return items


@login_required
def article_index(request):
    """
    JOIN implementation.

    select_related('outlet', 'category') makes Django retrieve every article
    together with its outlet and category in a single SQL statement, joining
    news_article to news_outlet and news_category.
    """
    articles = (
        Article.objects
        .select_related('outlet', 'category')
        .order_by('-published_at')
    )

    return render(request, 'insights/article_index.html', {
        'articles': articles,
        'generated_sql': _format_sql(articles) if request.GET.get('sql') == '1' else None,
    })


@login_required
def summarized_articles(request):
    """
    SUBQUERY implementation.

    The inner query collects the article IDs that have a row in news_summary.
    The outer query returns only articles whose ID appears in that result.
    """
    summary_article_ids = Summary.objects.values('article_id')
    articles = (
        Article.objects
        .filter(id__in=Subquery(summary_article_ids))
        .select_related('outlet', 'category')
        .prefetch_related('summary')
        .order_by('-published_at')
    )

    return render(request, 'insights/summarized_articles.html', {
        'articles': articles,
        'generated_sql': _format_sql(articles) if request.GET.get('sql') == '1' else None,
    })


@login_required
def outlet_breakdown(request):
    """
    GROUP BY + Aggregation (COUNT, AVG) implementation across Outlet and Category.
    """
    outlets = (
        Outlet.objects
        .select_related('category')
        .annotate(
            article_count=Count('articles', distinct=True),
            summary_count=Count('articles__summary', distinct=True),
            avg_read_minutes=Avg('articles__original_read_time_minutes'),
        )
        .order_by('-article_count', 'name')
    )
    categories = (
        Category.objects
        .annotate(
            article_count=Count('articles', distinct=True),
            summary_count=Count('articles__summary', distinct=True),
        )
        .order_by('-article_count', 'name')
    )
    generated_sql = _format_sql(outlets) if request.GET.get('sql') == '1' else None
    outlet_list = _attach_breakdown_percentages(list(outlets))
    category_list = _attach_breakdown_percentages(list(categories))
    return render(request, 'insights/outlet_breakdown.html', {
        'outlets': outlet_list,
        'categories': category_list,
        'generated_sql': generated_sql,
    })
