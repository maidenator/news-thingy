from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from news.models import Article, Category, Outlet, UserSubscription


def _redirect_back(request, fallback):
    referer = request.META.get('HTTP_REFERER')
    if referer and url_has_allowed_host_and_scheme(
        referer,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(referer)
    return redirect(fallback)


@login_required
def home_view(request):
    subscription, _ = UserSubscription.objects.get_or_create(user=request.user)
    active_category = request.GET.get('category', 'all')
    search_query = request.GET.get('q', '').strip()
    saved_only = request.GET.get('saved') == '1'

    articles = Article.objects.select_related('outlet', 'category', 'summary').all()
    if active_category != 'all':
        articles = articles.filter(category__slug=active_category)
    if saved_only:
        articles = articles.filter(bookmarked_by=request.user)
    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(outlet__name__icontains=search_query) |
            Q(summary__tldr__icontains=search_query)
        )
    articles = list(articles)
    user_bookmarked_ids = set(request.user.bookmarked_articles.values_list('id', flat=True))
    saved_count = len(user_bookmarked_ids)

    return render(request, 'home/home.html', {
        'subscription': subscription,
        'subscribed_outlet_ids': set(subscription.outlets.values_list('id', flat=True)),
        'user_bookmarked_ids': user_bookmarked_ids,
        'saved_count': saved_count,
        'saved_only': saved_only,
        'categories': Category.objects.all(),
        'outlets': Outlet.objects.all(),
        'articles': articles,
        'active_category': active_category,
        'search_query': search_query,
        'total_articles_count': len(articles),
        'total_minutes_saved': sum(a.summary.minutes_saved for a in articles if hasattr(a, 'summary')),
        'user_outlets_count': subscription.outlets.count(),
    })


@login_required
def toggle_bookmark_view(request, article_id):
    if request.method == 'POST':
        article = get_object_or_404(Article, id=article_id)
        if article.bookmarked_by.filter(id=request.user.id).exists():
            article.bookmarked_by.remove(request.user)
            messages.info(request, f'Removed "{article.title}" from your bookmarks.')
        else:
            article.bookmarked_by.add(request.user)
            messages.success(request, f'Saved "{article.title}" to your bookmarks.')
    return _redirect_back(request, 'home:home')


@login_required
def toggle_subscription_view(request, outlet_id):
    if request.method == 'POST':
        outlet = get_object_or_404(Outlet, id=outlet_id)
        subscription, _ = UserSubscription.objects.get_or_create(user=request.user)
        if subscription.outlets.filter(id=outlet.id).exists():
            subscription.outlets.remove(outlet); messages.info(request, f'Unfollowed {outlet.name}.')
        else:
            subscription.outlets.add(outlet); messages.success(request, f'Now following {outlet.name}.')
    return _redirect_back(request, 'home:home')
