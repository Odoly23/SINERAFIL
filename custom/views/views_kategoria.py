from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from config.decorators import allowed_users
from custom.forms import KategoriaForm
from custom.models import Kategoria


@login_required
@allowed_users(allowed_roles=['admin'])
def kategoria_list(request):
    objects = Kategoria.objects.all()
    context = {
        'objects': objects,
        'title': 'Kategoria Pesa',
        'legend': 'Kategoria Pesa',
        'link_antes': [{'link_name': "kategoria-list", 'link_text': "Kategoria Pesa"}],
    }
    return render(request, 'custom/list.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def kategoria_add(request):
    if request.method == 'POST':
        form = KategoriaForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = request.user
            instance.save()
            messages.success(request, 'Kategoria aumenta ona ho susesu!')
            return redirect('kategoria-list')
    else:
        form = KategoriaForm()
    context = {
        'form': form,
        'title': 'Aumenta Kategoria',
        'legend': 'Aumenta Kategoria',
        'link_antes': [{'link_name': "kategoria-list", 'link_text': "Kategoria Pesa"}],
    }
    return render(request, 'custom/form.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def kategoria_edit(request, pk):
    obj = get_object_or_404(Kategoria, pk=pk)
    form = KategoriaForm(request.POST or None, instance=obj)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.updated_by = request.user
        instance.updated_at = timezone.now()
        instance.save()
        messages.success(request, 'Kategoria atualiza ho susesu!')
        return redirect('kategoria-list')
    context = {
        'form': form,
        'title': 'Edita Kategoria',
        'legend': 'Edita Kategoria',
        'link_antes': [{'link_name': "kategoria-list", 'link_text': "Kategoria Pesa"}],
    }
    return render(request, 'custom/form.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def kategoria_delete(request, pk):
    obj = get_object_or_404(Kategoria, pk=pk)
    if request.method == 'POST':
        obj.delete()   # pesa ne'ebé uza kategoria ne'e sei fo kategoria mamuk (SET_NULL)
        messages.success(request, 'Kategoria hamoos ho susesu!')
        return redirect('kategoria-list')
    context = {
        'obj': obj,
        'title': 'Hamoos Kategoria',
        'legend': 'Hamoos Kategoria',
        'cancel_url': 'kategoria-list',
    }
    return render(request, 'custom/confirm_delete.html', context)
