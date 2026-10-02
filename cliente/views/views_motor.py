from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from cliente.forms import MotorForm
from cliente.models import Motor
from config.decorators import allowed_users

ROLES_READ = ['admin', 'mekaniku', 'nain']
ROLES_WRITE = ['admin', 'mekaniku']
LINK = [{'link_name': "motor-list", 'link_text': "Motór Kliente"}]


@login_required
@allowed_users(allowed_roles=ROLES_READ)
def motor_list(request):
    objects = Motor.objects.select_related('kliente')
    context = {
        'objects': objects,
        'title': 'Motór Kliente',
        'legend': 'Motór Kliente',
        'link_antes': LINK,
    }
    return render(request, 'cliente/motor_list.html', context)


@login_required
@allowed_users(allowed_roles=ROLES_WRITE)
def motor_add(request):
    if request.method == 'POST':
        form = MotorForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = request.user
            instance.save()
            messages.success(request, 'Motór Kliente aumenta ona ho susesu!')
            return redirect('motor-list')
    else:
        form = MotorForm()
    context = {
        'form': form,
        'title': 'Aumenta Motór',
        'legend': 'Aumenta Motór',
        'link_antes': LINK,
    }
    return render(request, 'cliente/form.html', context)


@login_required
@allowed_users(allowed_roles=ROLES_WRITE)
def motor_edit(request, pk):
    obj = get_object_or_404(Motor, pk=pk)
    form = MotorForm(request.POST or None, instance=obj)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.updated_by = request.user
        instance.updated_at = timezone.now()
        instance.save()
        messages.success(request, 'Dadus atualiza ho susesu!')
        return redirect('motor-list')
    context = {
        'form': form,
        'title': 'Edita Motór',
        'legend': 'Edita Motór',
        'link_antes': LINK,
    }
    return render(request, 'cliente/form.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def motor_delete(request, pk):
    obj = get_object_or_404(Motor, pk=pk)
    if request.method == 'POST':
        try:
            obj.delete()
            messages.success(request, 'Dadus hamoos ho susesu!')
        except ProtectedError:
            messages.error(request, "Dadus ne'e iha servisu rejistu ona, labele hamoos.")
        return redirect('motor-list')
    context = {
        'obj': obj,
        'title': 'Hamoos Motór',
        'legend': 'Hamoos Motór',
        'cancel_url': 'motor-list',
    }
    return render(request, 'cliente/confirm_delete.html', context)
