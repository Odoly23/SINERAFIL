from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from config.decorators import allowed_users
from servisu.forms import DespezaForm
from servisu.models import Despeza

LINK = [{'link_name': "despeza-list", 'link_text': "Despeza"}]


@login_required
@allowed_users(allowed_roles=['admin', 'nain'])
def despeza_list(request):
    context = {
        'objects': Despeza.objects.all(),
        'title': 'Despeza Ofisina',
        'legend': 'Despeza Ofisina',
        'link_antes': LINK,
    }
    return render(request, 'servisu/despeza_list.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def despeza_add(request):
    if request.method == 'POST':
        form = DespezaForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = request.user
            instance.save()
            messages.success(request, 'Despeza aumenta ona ho susesu!')
            return redirect('despeza-list')
    else:
        form = DespezaForm()
    context = {'form': form, 'title': 'Aumenta Despeza', 'legend': 'Aumenta Despeza', 'link_antes': LINK}
    return render(request, 'servisu/form.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def despeza_edit(request, pk):
    obj = get_object_or_404(Despeza, pk=pk)
    form = DespezaForm(request.POST or None, instance=obj)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.updated_by = request.user
        instance.updated_at = timezone.now()
        instance.save()
        messages.success(request, 'Despeza atualiza ho susesu!')
        return redirect('despeza-list')
    context = {'form': form, 'title': 'Edita Despeza', 'legend': 'Edita Despeza', 'link_antes': LINK}
    return render(request, 'servisu/form.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def despeza_delete(request, pk):
    obj = get_object_or_404(Despeza, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Despeza hamoos ho susesu!')
        return redirect('despeza-list')
    context = {
        'obj': obj,
        'title': 'Hamoos Despeza',
        'legend': 'Hamoos Despeza',
        'cancel_url': 'despeza-list',
    }
    return render(request, 'servisu/confirm_delete.html', context)
