from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from accounts.forms import CustomLoginForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home:home')
    form = CustomLoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        messages.success(request, f'Welcome back, {request.user.username}!')
        next_url = request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)
        return redirect('home:home')
    if request.method == 'POST':
        messages.error(request, 'Invalid username or password. Please try again.')
    return render(request, 'login/login.html', {'form': form})


@require_POST
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, 'You have been successfully logged out. See you next time!')
    return redirect('login:login')
