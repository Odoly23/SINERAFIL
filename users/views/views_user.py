from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from config.activity import log_activity
from config.decorators import allowed_users
from users.forms import UserForm
from users.models import ActivityLog, User

DEFAULT_PASSWORD = 'nerafil123'
LINK = [{'link_name': "u-list", 'link_text': "Lista Utilizador"}]


@login_required
@allowed_users(allowed_roles=['admin'])
def user_list(request):
    context = {
        'objects': User.objects.all(),
        'title': 'Lista Utilizador',
        'legend': 'Lista Utilizador',
        'link_antes': LINK,
    }
    return render(request, 'users/list.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def user_add(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            log_activity(request.user, 'Aumenta utilizadór %s' % user.username)
            messages.success(request, f'Utilizadór {user.username} aumenta ona ho susesu.')
            return redirect('u-list')
    else:
        form = UserForm()
    context = {'form': form, 'title': 'Aumenta Utilizadór', 'legend': 'Aumenta Utilizadór', 'link_antes': LINK}
    return render(request, 'users/form.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def user_edit(request, pk):
    obj = get_object_or_404(User, pk=pk)
    form = UserForm(request.POST or None, instance=obj)
    if form.is_valid():
        if obj.pk == request.user.pk and not form.cleaned_data['is_active']:
            form.add_error('is_active', "Ita labele desativa konta ne'ebé uza agora.")
        elif obj.pk == request.user.pk and form.cleaned_data['role'] != 'admin':
            form.add_error('role', "Ita labele hasai papél admin husi konta rasik.")
        else:
            user = form.save()
            log_activity(request.user, 'Edita utilizadór %s' % user.username)
            messages.success(request, 'Dadus utilizadór atualiza ho susesu!')
            return redirect('u-list')
    context = {'form': form, 'title': 'Edita Utilizadór', 'legend': 'Edita Utilizadór', 'link_antes': LINK}
    return render(request, 'users/form.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def reset_password(request, pk):
    obj = get_object_or_404(User, pk=pk)
    obj.set_password(DEFAULT_PASSWORD)
    obj.save()
    log_activity(request.user, 'Reset password utilizadór %s' % obj.username)
    messages.success(request, f'Password {obj.username} reset ona ba "{DEFAULT_PASSWORD}".')
    return redirect('u-list')


@login_required
@allowed_users(allowed_roles=['admin'])
def activity_log(request):
    context = {
        'objects': ActivityLog.objects.select_related('user')[:2000],
        'title': 'Log Atividade',
        'legend': 'Log Atividade Utilizadór',
        'link_antes': [{'link_name': "activity-log", 'link_text': "Log Atividade"}],
    }
    return render(request, 'users/activity_log.html', context)
