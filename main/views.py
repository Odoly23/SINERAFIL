from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render

from config.activity import log_activity


# ══════════════════════════════════════════════════════════════
#  ABOUT (pájina públiku)
# ══════════════════════════════════════════════════════════════

def about(request):
    return render(request, 'home/landing.html', {'title': 'Ofisina Nerafil'})


# ══════════════════════════════════════════════════════════════
#  LOGIN
# ══════════════════════════════════════════════════════════════

def loginPage(request):
    """Start -> System Login -> User Validation (valid: Dashboard; invalid: fila ba login)."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        if not username or not password:
            messages.warning(request, 'Username no password labele mamuk.')
            return render(request, 'auth/login.html', {'title': 'Pajina Login'})
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            log_activity(user, 'Login')
            messages.success(request, f'Bem-vindo, {user.display_name}!')
            nxt = request.GET.get('next') or request.POST.get('next')
            return redirect(nxt if nxt and nxt.startswith('/') else 'dashboard')
        messages.error(request, "Username ka password salah, ka konta la ativu. Favor koko fila fali.")
    return render(request, 'auth/login.html', {'title': 'Pajina Login'})


# ══════════════════════════════════════════════════════════════
#  LOGOUT
# ══════════════════════════════════════════════════════════════

def logout_view(request):
    if request.user.is_authenticated:
        log_activity(request.user, 'Logout')
        logout(request)
    return redirect('login')


# ══════════════════════════════════════════════════════════════
#  ERROR PAGES
# ══════════════════════════════════════════════════════════════

def error_404(request, exception):
    return render(request, 'auth/404.html', {}, status=404)


def error_500(request):
    return render(request, 'auth/500.html', {}, status=500)
