from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from users.forms import ChangePasswordForm
from users.models import AuditLogin, EmpUser


@login_required
def UserProfile(request):
    emp_user = EmpUser.objects.filter(user=request.user).select_related('emp').first()
    last_login = AuditLogin.objects.filter(user=request.user).order_by('-login_time')[:5]
    context = {
        'profile': emp_user.emp if emp_user else None,
        'last_login': last_login,
        'title': 'Profile Utilizador',
        'legend': 'Profile Utilizador',
    }
    return render(request, 'users/profile.html', context)


@login_required
def change_password(request):
    form = ChangePasswordForm(request.user, request.POST or None)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Password troka ona ho susesu!')
        return redirect('UserProfile')
    context = {
        'form': form,
        'title': 'Troka Password',
        'legend': 'Troka Password',
        'link_antes': [{'link_name': "UserProfile", 'link_text': "Profile"}],
    }
    return render(request, 'users/form.html', context)
