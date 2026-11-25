from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from config.activity import log_activity
from config.decorators import allowed_users
from inventory.forms import StockMovementForm
from inventory.models import StockMovement
from inventory.utils import StockError, register_movement

LINK = [{'link_name': "movement-list", 'link_text': "Stock In / Stock Out"}]


@login_required
@allowed_users(allowed_roles=['admin', 'owner'])
def movement_list(request):
    objects = StockMovement.objects.select_related('part')
    kind = request.GET.get('type', '')
    if kind in (StockMovement.IN, StockMovement.OUT):
        objects = objects.filter(movement_type=kind)
    context = {
        'objects': objects[:2000],
        'kind': kind,
        'title': 'Stock Tama / Sai',
        'legend': 'Stock Tama / Sai (Stock In / Stock Out)',
        'link_antes': LINK,
    }
    return render(request, 'inventory/movement_list.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def movement_add(request):
    if request.method == 'POST':
        form = StockMovementForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            try:
                register_movement(d['part'], d['movement_type'], d['quantity'], d['note'])
            except StockError as e:
                form.add_error('quantity', str(e))
            else:
                log_activity(request.user, 'Stock %s %s x%s' % (d['movement_type'], d['part'].sku, d['quantity']))
                messages.success(request, 'Stock atualiza ona ho susesu!')
                return redirect('movement-list')
    else:
        form = StockMovementForm()
    context = {'form': form, 'title': 'Rejistu Stock Tama / Sai', 'legend': 'Rejistu Stock Tama / Sai', 'link_antes': LINK}
    return render(request, 'inventory/form.html', context)
