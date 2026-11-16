from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render
from accounts.forms import CustomUserCreationForm
from news.models import Category, Outlet, UserSubscription


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home:home')
    form = CustomUserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        subscription, _ = UserSubscription.objects.get_or_create(user=user)
        subscription.outlets.set(Outlet.objects.all())
        subscription.categories.set(Category.objects.all())
        login(request, user)
        messages.success(request, f'Welcome to News Thingy, {user.username}! Your daily briefing is ready below.')
        return redirect('home:home')
    if request.method == 'POST':
        messages.error(request, 'Please correct the errors below to complete your registration.')
    return render(request, 'register/register.html', {'form': form})
