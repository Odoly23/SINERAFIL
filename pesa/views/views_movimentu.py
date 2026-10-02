from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from config.decorators import allowed_users
from pesa.forms import MovimentuForm
from pesa.models import MovimentuStock
from pesa.utils import StockError, register_movement


@login_required
@allowed_users(allowed_roles=['admin', 'nain'])
def movimentu_list(request):
    objects = MovimentuStock.objects.select_related('pesa', 'servisu')
    tipu = request.GET.get('tipu', '')
    if tipu in (MovimentuStock.TAMA, MovimentuStock.SAI):
        objects = objects.filter(tipu=tipu)
    context = {
        'objects': objects[:1000],
        'tipu': tipu,
        'title': 'Sasán Tama no Sai',
        'legend': 'Sasán Tama no Sai',
        'link_antes': [{'link_name': "movimentu-list", 'link_text': "Sasán Tama no Sai"}],
    }
    return render(request, 'pesa/movimentu_list.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def movimentu_add(request):
    if request.method == 'POST':
        form = MovimentuForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            extra = {'date': d['date'], 'reference': d['reference'], 'note': d['note']}
            if d.get('price'):
                extra['price'] = d['price']
            try:
                register_movement(d['pesa'], d['tipu'], d['quantity'], user=request.user, **extra)
            except StockError as e:
                form.add_error('quantity', str(e))
            else:
                messages.success(request, 'Movimentu stock rejistu ona ho susesu!')
                return redirect('movimentu-list')
    else:
        form = MovimentuForm()
    context = {
        'form': form,
        'title': 'Rejistu Sasán Tama / Sai',
        'legend': 'Rejistu Sasán Tama / Sai',
        'link_antes': [{'link_name': "movimentu-list", 'link_text': "Sasán Tama no Sai"}],
    }
    return render(request, 'pesa/form.html', context)
