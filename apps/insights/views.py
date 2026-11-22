from django.contrib.auth.decorators import login_required
from django.db.models import Subquery
from django.shortcuts import render

from news.models import Article, Summary


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
        'generated_sql': str(articles.query) if request.GET.get('sql') == '1' else None,
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
        'generated_sql': str(articles.query) if request.GET.get('sql') == '1' else None,
    })
