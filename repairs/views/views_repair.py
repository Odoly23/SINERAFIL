from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from config.activity import log_activity
from config.auth_utils import get_role
from config.decorators import allowed_users
from repairs.forms import AddPartForm, RepairForm
from repairs.models import Repair
from repairs.utils import can_operate, can_view, restore_parts, workflow_steps

ROLES_READ = ['admin', 'technician', 'owner']
LINK = [{'link_name': "repair-list", 'link_text': "Repair Management"}]


@login_required
@allowed_users(allowed_roles=ROLES_READ)
def repair_list(request):
    objects = (Repair.objects.select_related('customer', 'equipment', 'technician').prefetch_related('parts'))
    if get_role(request.user) == 'technician':
        objects = objects.filter(technician=request.user)
    status = request.GET.get('status', '')
    if status in dict(Repair.STATUS_CHOICES):
        objects = objects.filter(status=status)
    context = {
        'objects': objects[:2000],
        'status': status,
        'status_choices': Repair.STATUS_CHOICES,
        'title': 'Jestaun Reparasaun',
        'legend': 'Jestaun Reparasaun (Repair Management)',
        'link_antes': LINK,
    }
    return render(request, 'repairs/list.html', context)


@login_required
@allowed_users(allowed_roles=ROLES_READ)
def repair_detail(request, pk):
    obj = get_object_or_404(
        Repair.objects.select_related('customer', 'equipment', 'technician').prefetch_related('parts__part'), pk=pk)
    if not can_view(request.user, obj):
        return render(request, 'auth/404.html', status=403)
    role = get_role(request.user)
    operate = can_operate(request.user, obj)
    context = {
        'obj': obj,
        'steps': workflow_steps(obj),
        'can_operate': operate,
        'is_admin': role == 'admin',
        'can_use_parts': operate and obj.status in (Repair.ASSIGNED, Repair.IN_PROGRESS),
        'add_form': AddPartForm(),
        'title': 'Reparasaun %s' % obj.repair_number,
        'legend': 'Reparasaun %s' % obj.repair_number,
        'link_antes': LINK,
    }
    return render(request, 'repairs/detail.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def repair_add(request):
    """Etapa 1: Customer and Equipment Data -> Register New Repair."""
    if request.method == 'POST':
        form = RepairForm(request.POST)
        if form.is_valid():
            obj = form.save()
            log_activity(request.user, 'Rejistu reparasaun %s' % obj.repair_number)
            messages.success(request, "Reparasaun %s rejistu ona. Etapa tuir mai: Diagnóstiku estragu." % obj.repair_number)
            return redirect('repair-detail', pk=obj.pk)
    else:
        form = RepairForm()
    context = {'form': form, 'title': 'Rejistu Reparasaun Foun', 'legend': 'Rejistu Reparasaun Foun',
               'link_antes': LINK}
    return render(request, 'repairs/form.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def repair_edit(request, pk):
    obj = get_object_or_404(Repair, pk=pk)
    if obj.status == Repair.COMPLETED:
        messages.error(request, 'Reparasaun remata ona, labele edita.')
        return redirect('repair-detail', pk=pk)
    form = RepairForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        log_activity(request.user, 'Edita reparasaun %s' % obj.repair_number)
        messages.success(request, 'Reparasaun atualiza ho susesu!')
        return redirect('repair-detail', pk=pk)
    context = {'form': form, 'title': 'Edita Reparasaun %s' % obj.repair_number,
               'legend': 'Edita Reparasaun %s' % obj.repair_number, 'link_antes': LINK}
    return render(request, 'repairs/form.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
@transaction.atomic
def repair_delete(request, pk):
    obj = get_object_or_404(Repair, pk=pk)
    if request.method == 'POST':
        number = obj.repair_number
        restore_parts(obj)         # stock pesa fila fali
        obj.delete()
        log_activity(request.user, 'Hamoos reparasaun %s' % number)
        messages.success(request, 'Reparasaun hamoos ho susesu; stock fila ona.')
        return redirect('repair-list')
    context = {'obj': obj, 'title': 'Hamoos Reparasaun', 'legend': 'Hamoos Reparasaun', 'cancel_url': 'repair-list'}
    return render(request, 'repairs/confirm_delete.html', context)
