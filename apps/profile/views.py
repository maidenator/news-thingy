from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .forms import ProfileForm
from .models import Profile


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save(); messages.success(request, 'Your profile has been updated.')
        return redirect('profile:profile')
    return render(request, 'profile/profile.html', {'form': form, 'profile': profile})
