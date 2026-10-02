from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from config.decorators import allowed_users
from pesa.forms import PesaForm
from pesa.models import Pesa

ROLES_READ = ['admin', 'mekaniku', 'nain']


@login_required
@allowed_users(allowed_roles=ROLES_READ)
def pesa_list(request):
    objects = Pesa.objects.select_related('kategoria')
    low = bool(request.GET.get('low'))
    if low:
        objects = objects.filter(is_active=True, stock__lte=F('stock_min'))
    context = {
        'objects': objects,
        'low': low,
        'title': 'Pesa-Rezerva',
        'legend': 'Pesa-Rezerva',
        'link_antes': [{'link_name': "pesa-list", 'link_text': "Pesa-Rezerva"}],
    }
    return render(request, 'pesa/list.html', context)


@login_required
@allowed_users(allowed_roles=ROLES_READ)
def pesa_detail(request, pk):
    obj = get_object_or_404(Pesa.objects.select_related('kategoria'), pk=pk)
    context = {
        'obj': obj,
        'movimentu': obj.movimentu.select_related('servisu')[:50],
        'title': obj.name,
        'legend': 'Detallu Pesa',
        'link_antes': [{'link_name': "pesa-list", 'link_text': "Pesa-Rezerva"}],
    }
    return render(request, 'pesa/detail.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def pesa_add(request):
    if request.method == 'POST':
        form = PesaForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = request.user
            instance.save()
            messages.success(request, f'Pesa {instance.name} aumenta ona ho susesu!')
            return redirect('pesa-list')
    else:
        form = PesaForm()
    context = {
        'form': form,
        'title': 'Aumenta Pesa',
        'legend': 'Aumenta Pesa',
        'link_antes': [{'link_name': "pesa-list", 'link_text': "Pesa-Rezerva"}],
    }
    return render(request, 'pesa/form.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def pesa_edit(request, pk):
    obj = get_object_or_404(Pesa, pk=pk)
    form = PesaForm(request.POST or None, instance=obj)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.updated_by = request.user
        instance.updated_at = timezone.now()
        instance.save()
        messages.success(request, 'Dadus pesa atualiza ho susesu!')
        return redirect('pesa-list')
    context = {
        'form': form,
        'title': 'Edita Pesa',
        'legend': 'Edita Pesa',
        'link_antes': [{'link_name': "pesa-list", 'link_text': "Pesa-Rezerva"}],
    }
    return render(request, 'pesa/form.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def pesa_delete(request, pk):
    obj = get_object_or_404(Pesa, pk=pk)
    if request.method == 'POST':
        try:
            obj.delete()
            messages.success(request, 'Pesa hamoos ho susesu!')
        except ProtectedError:
            messages.error(request, "Pesa ne'e iha istória movimentu/servisu, labele hamoos. Desativa de'it.")
        return redirect('pesa-list')
    context = {
        'obj': obj,
        'title': 'Hamoos Pesa',
        'legend': 'Hamoos Pesa',
        'cancel_url': 'pesa-list',
    }
    return render(request, 'pesa/confirm_delete.html', context)
