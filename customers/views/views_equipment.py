from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from config.activity import log_activity
from config.decorators import allowed_users
from customers.forms import EquipmentForm
from customers.models import Equipment

ROLES_READ = ['admin', 'technician', 'owner']
ROLES_WRITE = ['admin', 'technician']
LINK = [{'link_name': "equipment-list", 'link_text': "Dadus Ekipamentu (Equipment)"}]


@login_required
@allowed_users(allowed_roles=ROLES_READ)
def equipment_list(request):
    context = {
        'objects': Equipment.objects.select_related('customer'),
        'title': 'Dadus Ekipamentu (Equipment)',
        'legend': 'Dadus Ekipamentu (Equipment)',
        'link_antes': LINK,
    }
    return render(request, 'customers/equipment_list.html', context)


@login_required
@allowed_users(allowed_roles=ROLES_WRITE)
def equipment_add(request):
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            obj = form.save()
            log_activity(request.user, 'Aumenta equipment %s' % obj)
            messages.success(request, 'Dadus aumenta ona ho susesu!')
            return redirect('equipment-list')
    else:
        form = EquipmentForm()
    context = {'form': form, 'title': 'Aumenta Ekipamentu', 'legend': 'Aumenta Ekipamentu', 'link_antes': LINK}
    return render(request, 'customers/form.html', context)


@login_required
@allowed_users(allowed_roles=ROLES_WRITE)
def equipment_edit(request, pk):
    obj = get_object_or_404(Equipment, pk=pk)
    form = EquipmentForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        log_activity(request.user, 'Edita equipment %s' % obj)
        messages.success(request, 'Dadus atualiza ho susesu!')
        return redirect('equipment-list')
    context = {'form': form, 'title': 'Edita Ekipamentu', 'legend': 'Edita Ekipamentu', 'link_antes': LINK}
    return render(request, 'customers/form.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def equipment_delete(request, pk):
    obj = get_object_or_404(Equipment, pk=pk)
    if request.method == 'POST':
        label = str(obj)
        try:
            obj.delete()
            log_activity(request.user, 'Hamoos equipment %s' % label)
            messages.success(request, 'Dadus hamoos ho susesu!')
        except ProtectedError:
            messages.error(request, "Dadus ne'e iha reparasaun rejistu ona, labele hamoos.")
        return redirect('equipment-list')
    context = {'obj': obj, 'title': 'Hamoos Ekipamentu', 'legend': 'Hamoos Ekipamentu', 'cancel_url': 'equipment-list'}
    return render(request, 'customers/confirm_delete.html', context)
