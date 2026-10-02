from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from config.auth_utils import get_emp, get_group
from config.decorators import allowed_users
from pesa.models import MovimentuStock
from pesa.utils import StockError, register_movement
from servisu.forms import AddPesaForm, ServisuForm
from servisu.models import Servisu, ServisuPesa
from servisu.utils import can_edit_servisu, can_view_servisu, restore_items

ROLES_READ = ['admin', 'mekaniku', 'nain']
ROLES_WRITE = ['admin', 'mekaniku']
LINK = [{'link_name': "servisu-list", 'link_text': "Servisu"}]


@login_required
@allowed_users(allowed_roles=ROLES_READ)
def servisu_list(request):
    objects = (Servisu.objects.select_related('kliente', 'motor', 'mekanik')
               .prefetch_related('items'))
    if get_group(request.user) == 'mekaniku':
        objects = objects.filter(mekanik=get_emp(request.user))
    status = request.GET.get('status', '')
    if status in dict(Servisu.STATUS_CHOICES):
        objects = objects.filter(status=status)
    context = {
        'objects': objects[:1000],
        'status': status,
        'status_choices': Servisu.STATUS_CHOICES,
        'title': 'Servisu Reparasaun',
        'legend': 'Servisu Reparasaun',
        'link_antes': LINK,
    }
    return render(request, 'servisu/list.html', context)


@login_required
@allowed_users(allowed_roles=ROLES_READ)
def servisu_detail(request, pk):
    obj = get_object_or_404(
        Servisu.objects.select_related('kliente', 'motor', 'mekanik').prefetch_related('items__pesa'), pk=pk)
    if not can_view_servisu(request.user, obj):
        return render(request, 'auth/404.html', status=403)
    context = {
        'obj': obj,
        'can_edit': can_edit_servisu(request.user, obj),
        'add_form': AddPesaForm(),
        'title': 'Servisu %s' % obj.invoice_no,
        'legend': 'Servisu %s' % obj.invoice_no,
        'link_antes': LINK,
    }
    return render(request, 'servisu/detail.html', context)


@login_required
@allowed_users(allowed_roles=ROLES_WRITE)
def servisu_add(request):
    group = get_group(request.user)
    if request.method == 'POST':
        form = ServisuForm(request.POST, emp=get_emp(request.user), group=group)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = request.user
            instance.save()
            messages.success(request, "Servisu %s kria ona. Aumenta pesa ne'ebé uza." % instance.invoice_no)
            return redirect('servisu-detail', pk=instance.pk)
    else:
        form = ServisuForm(emp=get_emp(request.user), group=group)
    context = {
        'form': form,
        'title': 'Servisu Foun',
        'legend': 'Servisu Foun',
        'link_antes': LINK,
    }
    return render(request, 'servisu/form.html', context)


@login_required
@allowed_users(allowed_roles=ROLES_WRITE)
def servisu_edit(request, pk):
    obj = get_object_or_404(Servisu, pk=pk)
    if not can_edit_servisu(request.user, obj):
        return render(request, 'auth/404.html', status=403)
    form = ServisuForm(request.POST or None, instance=obj,
                       emp=get_emp(request.user), group=get_group(request.user))
    if form.is_valid():
        instance = form.save(commit=False)
        instance.updated_by = request.user
        instance.updated_at = timezone.now()
        instance.save()
        messages.success(request, 'Servisu atualiza ho susesu!')
        return redirect('servisu-detail', pk=obj.pk)
    context = {
        'form': form,
        'title': 'Edita Servisu %s' % obj.invoice_no,
        'legend': 'Edita Servisu %s' % obj.invoice_no,
        'link_antes': LINK,
    }
    return render(request, 'servisu/form.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
@transaction.atomic
def servisu_delete(request, pk):
    obj = get_object_or_404(Servisu, pk=pk)
    if request.method == 'POST':
        restore_items(obj, request.user)     # fila stock pesa hotu-hotu
        obj.delete()
        messages.success(request, 'Servisu hamoos ho susesu; stock fila ona.')
        return redirect('servisu-list')
    context = {
        'obj': obj,
        'title': 'Hamoos Servisu',
        'legend': 'Hamoos Servisu',
        'cancel_url': 'servisu-list',
    }
    return render(request, 'servisu/confirm_delete.html', context)


@login_required
@allowed_users(allowed_roles=ROLES_WRITE)
@require_POST
def servisu_pesa_add(request, pk):
    servisu = get_object_or_404(Servisu, pk=pk)
    if not can_edit_servisu(request.user, servisu):
        return render(request, 'auth/404.html', status=403)
    form = AddPesaForm(request.POST)
    if form.is_valid():
        pesa, qty = form.cleaned_data['pesa'], form.cleaned_data['quantity']
        try:
            with transaction.atomic():
                register_movement(
                    pesa, MovimentuStock.SAI, qty, user=request.user,
                    reference=servisu.invoice_no, servisu=servisu,
                    note='Uza iha servisu %s' % servisu.invoice_no)
                item, _ = ServisuPesa.objects.get_or_create(
                    servisu=servisu, pesa=pesa,
                    defaults={'quantity': 0, 'price_buy': pesa.price_buy, 'price_sell': pesa.price_sell})
                item.quantity += qty
                item.save()
            messages.success(request, 'Pesa "%s" aumenta ona; stock redús ho %s.' % (pesa.name, qty))
        except StockError as e:
            messages.error(request, str(e))
    else:
        messages.error(request, "Hili pesa no kuantidade ne'ebé loos.")
    return redirect('servisu-detail', pk=pk)


@login_required
@allowed_users(allowed_roles=ROLES_WRITE)
@require_POST
def servisu_pesa_remove(request, pk, item_pk):
    servisu = get_object_or_404(Servisu, pk=pk)
    if not can_edit_servisu(request.user, servisu):
        return render(request, 'auth/404.html', status=403)
    item = get_object_or_404(ServisuPesa, pk=item_pk, servisu=servisu)
    with transaction.atomic():
        register_movement(
            item.pesa, MovimentuStock.TAMA, item.quantity, user=request.user,
            price=item.price_buy, reference=servisu.invoice_no, servisu=servisu,
            note='Hasai husi servisu %s' % servisu.invoice_no)
        item.delete()
    messages.success(request, 'Pesa hasai ona; stock fila fali.')
    return redirect('servisu-detail', pk=pk)
