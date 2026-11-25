from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from config.activity import log_activity
from config.decorators import allowed_users
from custom.forms import SupplierForm
from custom.models import Supplier

LINK = [{'link_name': "supplier-list", 'link_text': "Supplier"}]


@login_required
@allowed_users(allowed_roles=['admin'])
def supplier_list(request):
    context = {
        'objects': Supplier.objects.all(),
        'title': 'Supplier',
        'legend': 'Supplier',
        'link_antes': LINK,
    }
    return render(request, 'custom/supplier_list.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def supplier_add(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            obj = form.save()
            log_activity(request.user, 'Aumenta supplier %s' % obj.name)
            messages.success(request, 'Supplier aumenta ona ho susesu!')
            return redirect('supplier-list')
    else:
        form = SupplierForm()
    context = {'form': form, 'title': 'Aumenta Supplier', 'legend': 'Aumenta Supplier', 'link_antes': LINK}
    return render(request, 'custom/form.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def supplier_edit(request, pk):
    obj = get_object_or_404(Supplier, pk=pk)
    form = SupplierForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        log_activity(request.user, 'Edita supplier %s' % obj.name)
        messages.success(request, 'Dadus atualiza ho susesu!')
        return redirect('supplier-list')
    context = {'form': form, 'title': 'Edita Supplier', 'legend': 'Edita Supplier', 'link_antes': LINK}
    return render(request, 'custom/form.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def supplier_delete(request, pk):
    obj = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        name = obj.name
        obj.delete()    # pesa ne'ebé uza ne'e sei sai mamuk (SET_NULL)
        log_activity(request.user, 'Hamoos supplier %s' % name)
        messages.success(request, 'Dadus hamoos ho susesu!')
        return redirect('supplier-list')
    context = {'obj': obj, 'title': 'Hamoos Supplier', 'legend': 'Hamoos Supplier', 'cancel_url': 'supplier-list'}
    return render(request, 'custom/confirm_delete.html', context)
