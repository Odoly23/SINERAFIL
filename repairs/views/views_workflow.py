"""Etapa reparasaun tuir flowchart: Diagnosis -> Assign -> Spare Parts -> Process -> Completion."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from config.activity import log_activity
from config.decorators import allowed_users
from repairs.forms import AddPartForm, AssignForm, CompleteForm, DiagnosisForm
from repairs.models import Repair, RepairPart
from repairs.utils import RepairError, add_part, can_operate, remove_part
from inventory.utils import StockError

ROLES_WORK = ['admin', 'technician']


def _link(repair):
    return [{'link_name': "repair-list", 'link_text': "Repair Management"},
            {'link_name': "repair-detail", 'link_param': repair.pk, 'link_text': repair.repair_number}]


def _forbidden(request):
    return render(request, 'auth/404.html', status=403)


def _step_page(request, repair, form, title):
    context = {'form': form, 'obj': repair, 'title': title, 'legend': title, 'link_antes': _link(repair)}
    return render(request, 'repairs/form.html', context)


@login_required
@allowed_users(allowed_roles=ROLES_WORK)
def repair_diagnose(request, pk):
    """Etapa 2: Damage Diagnosis."""
    repair = get_object_or_404(Repair, pk=pk)
    if not can_operate(request.user, repair):
        return _forbidden(request)
    form = DiagnosisForm(request.POST or None, instance=repair)
    if form.is_valid():
        obj = form.save(commit=False)
        if obj.status == Repair.REGISTERED:
            obj.status = Repair.DIAGNOSED
        obj.save()
        log_activity(request.user, 'Diagnóstiku %s' % obj.repair_number)
        messages.success(request, 'Diagnóstiku rai ona. Etapa tuir mai: Hili mekániku.')
        return redirect('repair-detail', pk=pk)
    return _step_page(request, repair, form, 'Damage Diagnosis — %s' % repair.repair_number)


@login_required
@allowed_users(allowed_roles=['admin'])
def repair_assign(request, pk):
    """Etapa 3: Assign Technician (bele troka molok reparasaun hahú)."""
    repair = get_object_or_404(Repair, pk=pk)
    if repair.status not in (Repair.DIAGNOSED, Repair.ASSIGNED):
        messages.error(request, 'Hili mekániku bele halo de\'it depois diagnóstiku no molok reparasaun hahú.')
        return redirect('repair-detail', pk=pk)
    form = AssignForm(request.POST or None, instance=repair)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.status = Repair.ASSIGNED
        obj.save()
        log_activity(request.user, 'Hili mekániku %s ba %s' % (obj.technician.username, obj.repair_number))
        messages.success(request, 'Mekániku hili ona. Agora bele uza pesa.')
        return redirect('repair-detail', pk=pk)
    return _step_page(request, repair, form, 'Assign Technician — %s' % repair.repair_number)


@login_required
@allowed_users(allowed_roles=ROLES_WORK)
@require_POST
def repair_part_add(request, pk):
    """Etapa 4: Spare Parts Usage -> Automatic Stock Update."""
    repair = get_object_or_404(Repair, pk=pk)
    if not can_operate(request.user, repair):
        return _forbidden(request)
    form = AddPartForm(request.POST)
    if form.is_valid():
        d = form.cleaned_data
        try:
            add_part(repair, d['part'], d['quantity'], d['unit_price'])
            log_activity(request.user, 'Uza pesa %s x%s iha %s' % (d['part'].sku, d['quantity'], repair.repair_number))
            messages.success(request, 'Pesa "%s" aumenta ona; stock redús ho %s.' % (d['part'].name, d['quantity']))
        except (RepairError, StockError) as e:
            messages.error(request, str(e))
    else:
        messages.error(request, "Hili pesa no kuantidade ne'ebé loos.")
    return redirect('repair-detail', pk=pk)


@login_required
@allowed_users(allowed_roles=ROLES_WORK)
@require_POST
def repair_part_remove(request, pk, item_pk):
    repair = get_object_or_404(Repair, pk=pk)
    if not can_operate(request.user, repair):
        return _forbidden(request)
    item = get_object_or_404(RepairPart, pk=item_pk, repair=repair)
    log_activity(request.user, 'Hasai pesa %s husi %s' % (item.part.sku, repair.repair_number))
    remove_part(repair, item)
    messages.success(request, 'Pesa hasai ona; stock fila fali.')
    return redirect('repair-detail', pk=pk)


@login_required
@allowed_users(allowed_roles=ROLES_WORK)
@require_POST
def repair_start(request, pk):
    """Etapa 5: Repair Process."""
    repair = get_object_or_404(Repair, pk=pk)
    if not can_operate(request.user, repair):
        return _forbidden(request)
    if repair.status != Repair.ASSIGNED:
        messages.error(request, 'Reparasaun bele hahú de\'it depois mekániku hili.')
    else:
        repair.status = Repair.IN_PROGRESS
        repair.save(update_fields=['status'])
        log_activity(request.user, 'Hahú prosesu %s' % repair.repair_number)
        messages.success(request, 'Prosesu reparasaun hahú ona.')
    return redirect('repair-detail', pk=pk)


@login_required
@allowed_users(allowed_roles=ROLES_WORK)
def repair_complete(request, pk):
    """Etapa 6: Confirm Completion."""
    repair = get_object_or_404(Repair, pk=pk)
    if not can_operate(request.user, repair):
        return _forbidden(request)
    if repair.status != Repair.IN_PROGRESS:
        messages.error(request, 'Konfirmasaun remata bele halo de\'it bainhira reparasaun iha prosesu.')
        return redirect('repair-detail', pk=pk)
    form = CompleteForm(request.POST or None, instance=repair)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.status = Repair.COMPLETED
        obj.save()
        log_activity(request.user, 'Konfirma remata %s' % obj.repair_number)
        messages.success(request, 'Reparasaun remata ona. Invoice/nota bele print.')
        return redirect('repair-detail', pk=pk)
    return _step_page(request, repair, form, 'Confirm Completion — %s' % repair.repair_number)
