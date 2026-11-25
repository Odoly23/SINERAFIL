from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from config.activity import log_activity
from users.forms import ChangePasswordForm
from users.models import ActivityLog


@login_required
def UserProfile(request):
    context = {
        'last_login': ActivityLog.objects.filter(user=request.user, action='Login')[:5],
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
        log_activity(user, 'Troka password')
        messages.success(request, 'Password troka ona ho susesu!')
        return redirect('UserProfile')
    context = {
        'form': form,
        'title': 'Troka Password',
        'legend': 'Troka Password',
        'link_antes': [{'link_name': "UserProfile", 'link_text': "Profile"}],
    }
    return render(request, 'users/form.html', context)
