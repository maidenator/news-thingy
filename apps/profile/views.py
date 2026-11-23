from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from news.models import UserSubscription
from .forms import ProfileForm
from .models import Profile


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save(); messages.success(request, 'Your profile has been updated.')
        return redirect('profile:profile')

    read_articles = list(request.user.read_articles.select_related('summary').all())
    subscription = UserSubscription.objects.filter(user=request.user).first()
    stats = {
        'stories_read': len(read_articles),
        'minutes_saved': sum(a.summary.minutes_saved for a in read_articles if hasattr(a, 'summary')),
        'bookmarks': request.user.bookmarked_articles.count(),
        'followed_outlets': subscription.outlets.count() if subscription else 0,
    }
    return render(request, 'profile/profile.html', {
        'form': form,
        'profile': profile,
        'stats': stats,
    })
