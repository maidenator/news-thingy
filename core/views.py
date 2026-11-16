from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from news.models import Category, Outlet, Article, UserSubscription


@login_required(login_url='accounts:login')
def home_view(request):
    """
    Editorial Front Page Briefing.
    Displays curated news summaries, category filters, outlet subscriptions,
    and reading time saved metrics.
    """
    # Ensure user has a subscription record
    subscription, _ = UserSubscription.objects.get_or_create(user=request.user)

    categories = Category.objects.all()
    outlets = Outlet.objects.all()

    # Query filtering
    active_category = request.GET.get('category', 'all')
    active_outlet = request.GET.get('outlet', 'all')

    articles_qs = Article.objects.select_related('outlet', 'category', 'summary').all()

    if active_category and active_category != 'all':
        articles_qs = articles_qs.filter(category__slug=active_category)

    if active_outlet and active_outlet != 'all':
        articles_qs = articles_qs.filter(outlet__slug=active_outlet)

    articles = list(articles_qs)

    # Calculate metrics
    total_minutes_saved = sum(
        getattr(article, 'summary', None).minutes_saved
        for article in articles
        if hasattr(article, 'summary')
    )
    user_outlets_count = subscription.outlets.count()

    context = {
        'user': request.user,
        'subscription': subscription,
        'subscribed_outlet_ids': set(subscription.outlets.values_list('id', flat=True)),
        'categories': categories,
        'outlets': outlets,
        'articles': articles,
        'active_category': active_category,
        'active_outlet': active_outlet,
        'total_minutes_saved': total_minutes_saved,
        'user_outlets_count': user_outlets_count,
        'total_articles_count': len(articles),
    }
    return render(request, 'core/home.html', context)


@login_required(login_url='accounts:login')
def toggle_subscription_view(request, outlet_id):
    """Allows subscribers to follow or unfollow specific news outlets."""
    if request.method == 'POST':
        outlet = get_object_or_404(Outlet, id=outlet_id)
        subscription, _ = UserSubscription.objects.get_or_create(user=request.user)

        if subscription.outlets.filter(id=outlet.id).exists():
            subscription.outlets.remove(outlet)
            messages.info(request, f"Unfollowed {outlet.name}.")
        else:
            subscription.outlets.add(outlet)
            messages.success(request, f"Now following {outlet.name}.")

    return redirect(request.META.get('HTTP_REFERER', 'core:home'))
