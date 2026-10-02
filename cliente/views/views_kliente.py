from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from cliente.forms import KlienteForm
from cliente.models import Kliente
from config.decorators import allowed_users

ROLES_READ = ['admin', 'mekaniku', 'nain']
ROLES_WRITE = ['admin', 'mekaniku']
LINK = [{'link_name': "kliente-list", 'link_text': "Kliente"}]


@login_required
@allowed_users(allowed_roles=ROLES_READ)
def kliente_list(request):
    objects = Kliente.objects.all()
    context = {
        'objects': objects,
        'title': 'Kliente',
        'legend': 'Kliente',
        'link_antes': LINK,
    }
    return render(request, 'cliente/kliente_list.html', context)


@login_required
@allowed_users(allowed_roles=ROLES_WRITE)
def kliente_add(request):
    if request.method == 'POST':
        form = KlienteForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = request.user
            instance.save()
            messages.success(request, 'Kliente aumenta ona ho susesu!')
            return redirect('kliente-list')
    else:
        form = KlienteForm()
    context = {
        'form': form,
        'title': 'Aumenta Kliente',
        'legend': 'Aumenta Kliente',
        'link_antes': LINK,
    }
    return render(request, 'cliente/form.html', context)


@login_required
@allowed_users(allowed_roles=ROLES_WRITE)
def kliente_edit(request, pk):
    obj = get_object_or_404(Kliente, pk=pk)
    form = KlienteForm(request.POST or None, instance=obj)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.updated_by = request.user
        instance.updated_at = timezone.now()
        instance.save()
        messages.success(request, 'Dadus atualiza ho susesu!')
        return redirect('kliente-list')
    context = {
        'form': form,
        'title': 'Edita Kliente',
        'legend': 'Edita Kliente',
        'link_antes': LINK,
    }
    return render(request, 'cliente/form.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def kliente_delete(request, pk):
    obj = get_object_or_404(Kliente, pk=pk)
    if request.method == 'POST':
        try:
            obj.delete()
            messages.success(request, 'Dadus hamoos ho susesu!')
        except ProtectedError:
            messages.error(request, "Dadus ne'e iha servisu rejistu ona, labele hamoos.")
        return redirect('kliente-list')
    context = {
        'obj': obj,
        'title': 'Hamoos Kliente',
        'legend': 'Hamoos Kliente',
        'cancel_url': 'kliente-list',
    }
    return render(request, 'cliente/confirm_delete.html', context)
