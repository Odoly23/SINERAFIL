from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from config.activity import log_activity
from config.decorators import allowed_users
from inventory.forms import PartForm
from inventory.models import Part

ROLES_READ = ['admin', 'technician', 'owner']
LINK = [{'link_name': "part-list", 'link_text': "Spare Parts Data"}]


@login_required
@allowed_users(allowed_roles=ROLES_READ)
def part_list(request):
    objects = Part.objects.select_related('category', 'supplier')
    low = bool(request.GET.get('low'))
    if low:
        objects = objects.filter(stock__lte=F('minimum_stock'))
    context = {
        'objects': objects,
        'low': low,
        'title': 'Dadus Pesa-Rezerva',
        'legend': 'Dadus Pesa-Rezerva (Spare Parts Data)',
        'link_antes': LINK,
    }
    return render(request, 'inventory/part_list.html', context)


@login_required
@allowed_users(allowed_roles=ROLES_READ)
def part_detail(request, pk):
    obj = get_object_or_404(Part.objects.select_related('category', 'supplier'), pk=pk)
    context = {
        'obj': obj,
        'movements': obj.movements.all()[:50],
        'title': obj.name,
        'legend': 'Detallu Pesa',
        'link_antes': LINK,
    }
    return render(request, 'inventory/part_detail.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def part_add(request):
    if request.method == 'POST':
        form = PartForm(request.POST)
        if form.is_valid():
            obj = form.save()
            log_activity(request.user, 'Aumenta pesa %s' % obj.sku)
            messages.success(request, f'Pesa {obj.name} aumenta ona ho susesu! Uza "Stock Tama" atu tau stock inísiu.')
            return redirect('part-list')
    else:
        form = PartForm()
    context = {'form': form, 'title': 'Aumenta Pesa', 'legend': 'Aumenta Pesa', 'link_antes': LINK}
    return render(request, 'inventory/form.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def part_edit(request, pk):
    obj = get_object_or_404(Part, pk=pk)
    form = PartForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        log_activity(request.user, 'Edita pesa %s' % obj.sku)
        messages.success(request, 'Dadus pesa atualiza ho susesu!')
        return redirect('part-list')
    context = {'form': form, 'title': 'Edita Pesa', 'legend': 'Edita Pesa', 'link_antes': LINK}
    return render(request, 'inventory/form.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def part_delete(request, pk):
    obj = get_object_or_404(Part, pk=pk)
    if request.method == 'POST':
        sku = obj.sku
        try:
            obj.delete()
            log_activity(request.user, 'Hamoos pesa %s' % sku)
            messages.success(request, 'Pesa hamoos ho susesu!')
        except ProtectedError:
            messages.error(request, "Pesa ne'e iha istória movimentu/reparasaun, labele hamoos.")
        return redirect('part-list')
    context = {'obj': obj, 'title': 'Hamoos Pesa', 'legend': 'Hamoos Pesa', 'cancel_url': 'part-list'}
    return render(request, 'inventory/confirm_delete.html', context)
