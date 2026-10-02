from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from config.auth_utils import get_group
from users.models import AuditLogin


# ══════════════════════════════════════════════════════════════
#  HELPER
# ══════════════════════════════════════════════════════════════

def _get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


# ══════════════════════════════════════════════════════════════
#  LANDING (pájina públiku)
# ══════════════════════════════════════════════════════════════

def landing(request):
    return render(request, 'home/landing.html', {'title': 'Ofisina Nerafil'})


# ══════════════════════════════════════════════════════════════
#  LOGIN
# ══════════════════════════════════════════════════════════════

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        if not username or not password:
            messages.warning(request, 'Username no password labele mamuk.')
            return render(request, 'auth/login.html', {'title': 'Pajina Login'})
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_active:
                messages.error(request, "Konta ne'e desativadu. Kontaktu administrador.")
                return render(request, 'auth/login.html', {'title': 'Pajina Login'})
            login(request, user)
            AuditLogin.objects.create(
                user=user,
                ip_address=_get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                user_type=get_group(user),
                is_active=True,
            )
            messages.success(request, f'Bem-vindo, {user.get_full_name() or user.username}!')
            return redirect(request.GET.get('next') or 'home')
        messages.error(request, 'Username ka password salah. Favor koko fila fali.')
    return render(request, 'auth/login.html', {'title': 'Pajina Login'})


# ══════════════════════════════════════════════════════════════
#  LOGOUT
# ══════════════════════════════════════════════════════════════

def logout_view(request):
    if request.user.is_authenticated:
        audit = AuditLogin.objects.filter(user=request.user, is_active=True).order_by('-login_time').first()
        if audit:
            audit.logout_time = timezone.now()
            audit.save()
        logout(request)
    return redirect('login')


# ══════════════════════════════════════════════════════════════
#  HOME — pájina sambutan semua user
# ══════════════════════════════════════════════════════════════

@login_required
def home(request):
    context = {
        'title': 'Sistema Jestaun Inventáriu',
        'legend': 'Bem-vindo',
        'homeactive': 'active',
    }
    return render(request, 'home/home.html', context)


# ══════════════════════════════════════════════════════════════
#  ERROR PAGES
# ══════════════════════════════════════════════════════════════

def error_404(request, exception):
    return render(request, 'auth/404.html', {}, status=404)


def error_500(request):
    return render(request, 'auth/500.html', {}, status=500)
