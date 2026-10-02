from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from config.decorators import allowed_users
from users.forms import EmpForm
from users.models import Emp, EmpUser
from users.utils import save_emp_account

DEFAULT_PASSWORD = 'nerafil123'


@login_required
@allowed_users(allowed_roles=['admin'])
def PList(request):
    objects = EmpUser.objects.select_related('emp', 'user').prefetch_related('user__groups').all()
    context = {
        'objects': objects,
        'title': 'Lista Utilizador',
        'legend': 'Lista Utilizador',
        'link_antes': [{'link_name': "u-list", 'link_text': "Lista Utilizador"}],
    }
    return render(request, 'users/list.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def emp_detail(request, pk):
    emp = get_object_or_404(Emp, pk=pk)
    empuser = getattr(emp, 'account', None)
    context = {
        'obj': emp,
        'empuser': empuser,
        'title': 'Detallu Funcionariu',
        'legend': 'Detallu Funcionariu',
        'link_antes': [{'link_name': "u-list", 'link_text': "Lista Utilizador"}],
    }
    return render(request, 'users/detail.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
@transaction.atomic
def EmpAdd(request):
    if request.method == 'POST':
        form = EmpForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = request.user
            instance.save()
            d = form.cleaned_data
            save_emp_account(instance, d['username'], d['group'], d['password'], d['is_active'])
            messages.success(request, f'Funcionariu {instance.name} aumenta ona ho susesu.')
            return redirect('emp-detail', pk=instance.pk)
    else:
        form = EmpForm()
    context = {
        'form': form,
        'title': 'Aumenta Funcionariu',
        'legend': 'Aumenta Funcionariu',
        'link_antes': [{'link_name': "u-list", 'link_text': "Lista Utilizador"}],
    }
    return render(request, 'users/form.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
@transaction.atomic
def emp_update(request, pk):
    emp = get_object_or_404(Emp, pk=pk)
    form = EmpForm(request.POST or None, instance=emp)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.updated_by = request.user
        instance.updated_at = timezone.now()
        instance.save()
        d = form.cleaned_data
        save_emp_account(instance, d['username'], d['group'], d['password'], d['is_active'])
        messages.success(request, 'Dadus Funcionariu atualiza ho susesu!')
        return redirect('emp-detail', pk=emp.pk)
    context = {
        'form': form,
        'obj': emp,
        'title': 'Atualiza Dadus Funcionariu',
        'legend': 'Atualiza Dadus Funcionariu',
        'link_antes': [{'link_name': "u-list", 'link_text': "Lista Utilizador"}],
    }
    return render(request, 'users/form.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def emp_delete(request, pk):
    emp = get_object_or_404(Emp, pk=pk)
    empuser = getattr(emp, 'account', None)
    if empuser and empuser.user_id == request.user.pk:
        messages.error(request, "Ita labele hamoos konta ne'ebé uza agora.")
        return redirect('u-list')
    if request.method == 'POST':
        from django.db.models import ProtectedError
        try:
            with transaction.atomic():
                if empuser and empuser.user:
                    empuser.user.delete()
                emp.delete()
        except ProtectedError:
            messages.error(request, "Funcionariu ne'e iha servisu rejistu ona, labele hamoos. Desativa de'it konta.")
            return redirect('u-list')
        messages.success(request, 'Funcionariu hamoos ho susesu!')
        return redirect('u-list')
    context = {
        'obj': emp,
        'title': 'Hamoos Funcionariu',
        'legend': 'Hamoos Funcionariu',
        'cancel_url': 'u-list',
    }
    return render(request, 'users/confirm_delete.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def reset_password(request, pk):
    empuser = get_object_or_404(EmpUser.objects.select_related('user'), pk=pk)
    empuser.user.set_password(DEFAULT_PASSWORD)
    empuser.user.save()
    messages.success(request, f'Password {empuser.user.username} reset ona ba "{DEFAULT_PASSWORD}".')
    return redirect('u-list')
