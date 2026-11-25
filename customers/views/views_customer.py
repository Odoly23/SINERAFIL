from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from config.activity import log_activity
from config.decorators import allowed_users
from customers.forms import CustomerForm
from customers.models import Customer

ROLES_READ = ['admin', 'technician', 'owner']
ROLES_WRITE = ['admin', 'technician']
LINK = [{'link_name': "customer-list", 'link_text': "Dadus Kliente (Customer)"}]


@login_required
@allowed_users(allowed_roles=ROLES_READ)
def customer_list(request):
    context = {
        'objects': Customer.objects.all(),
        'title': 'Dadus Kliente (Customer)',
        'legend': 'Dadus Kliente (Customer)',
        'link_antes': LINK,
    }
    return render(request, 'customers/customer_list.html', context)


@login_required
@allowed_users(allowed_roles=ROLES_WRITE)
def customer_add(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            obj = form.save()
            log_activity(request.user, 'Aumenta customer %s' % obj)
            messages.success(request, 'Dadus aumenta ona ho susesu!')
            return redirect('customer-list')
    else:
        form = CustomerForm()
    context = {'form': form, 'title': 'Aumenta Kliente', 'legend': 'Aumenta Kliente', 'link_antes': LINK}
    return render(request, 'customers/form.html', context)


@login_required
@allowed_users(allowed_roles=ROLES_WRITE)
def customer_edit(request, pk):
    obj = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        log_activity(request.user, 'Edita customer %s' % obj)
        messages.success(request, 'Dadus atualiza ho susesu!')
        return redirect('customer-list')
    context = {'form': form, 'title': 'Edita Kliente', 'legend': 'Edita Kliente', 'link_antes': LINK}
    return render(request, 'customers/form.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def customer_delete(request, pk):
    obj = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        label = str(obj)
        try:
            obj.delete()
            log_activity(request.user, 'Hamoos customer %s' % label)
            messages.success(request, 'Dadus hamoos ho susesu!')
        except ProtectedError:
            messages.error(request, "Dadus ne'e iha reparasaun rejistu ona, labele hamoos.")
        return redirect('customer-list')
    context = {'obj': obj, 'title': 'Hamoos Kliente', 'legend': 'Hamoos Kliente', 'cancel_url': 'customer-list'}
    return render(request, 'customers/confirm_delete.html', context)
