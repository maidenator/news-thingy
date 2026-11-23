from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from news.models import Category, Outlet, UserSubscription
from .forms import CustomLoginForm, CustomUserCreationForm


def register_view(request):
    """Handles new user registration."""
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Initialize subscription preferences with all outlets by default
            subscription, _ = UserSubscription.objects.get_or_create(user=user)
            subscription.outlets.set(Outlet.objects.all())
            subscription.categories.set(Category.objects.all())

            # Direct auto-login for immediate onboarding into the briefing
            auth_login(request, user)
            messages.success(
                request,
                f"Welcome to News Thingy, {user.username}! Your daily briefing is ready below."
            )
            return redirect('core:home')
        else:
            messages.error(
                request,
                "Please correct the errors below to complete your registration."
            )
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Handles user login."""
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect('core:home')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = CustomLoginForm(request)

    return render(request, 'accounts/login.html', {'form': form})


@require_POST
def logout_view(request):
    """Handles user logout and redirects to login screen."""
    if request.user.is_authenticated:
        auth_logout(request)
        messages.info(request, "You have been successfully logged out. See you next time!")
    return redirect('accounts:login')
