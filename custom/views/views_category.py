from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from config.activity import log_activity
from config.decorators import allowed_users
from custom.forms import CategoryForm
from custom.models import Category

LINK = [{'link_name': "category-list", 'link_text': "Kategoria"}]


@login_required
@allowed_users(allowed_roles=['admin'])
def category_list(request):
    context = {
        'objects': Category.objects.all(),
        'title': 'Kategoria',
        'legend': 'Kategoria',
        'link_antes': LINK,
    }
    return render(request, 'custom/category_list.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            obj = form.save()
            log_activity(request.user, 'Aumenta category %s' % obj.name)
            messages.success(request, 'Kategoria aumenta ona ho susesu!')
            return redirect('category-list')
    else:
        form = CategoryForm()
    context = {'form': form, 'title': 'Aumenta Kategoria', 'legend': 'Aumenta Kategoria', 'link_antes': LINK}
    return render(request, 'custom/form.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def category_edit(request, pk):
    obj = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        log_activity(request.user, 'Edita category %s' % obj.name)
        messages.success(request, 'Dadus atualiza ho susesu!')
        return redirect('category-list')
    context = {'form': form, 'title': 'Edita Kategoria', 'legend': 'Edita Kategoria', 'link_antes': LINK}
    return render(request, 'custom/form.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def category_delete(request, pk):
    obj = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        name = obj.name
        obj.delete()    # pesa ne'ebé uza ne'e sei sai mamuk (SET_NULL)
        log_activity(request.user, 'Hamoos category %s' % name)
        messages.success(request, 'Dadus hamoos ho susesu!')
        return redirect('category-list')
    context = {'obj': obj, 'title': 'Hamoos Kategoria', 'legend': 'Hamoos Kategoria', 'cancel_url': 'category-list'}
    return render(request, 'custom/confirm_delete.html', context)
