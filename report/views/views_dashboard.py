from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.shortcuts import render
from django.utils import timezone

from config.auth_utils import get_emp, get_group
from config.decorators import allowed_users
from config.utils import first_day_of_month, month_start
from pesa.models import Pesa
from servisu.models import Despeza, Servisu, ServisuPesa


@login_required
@allowed_users(allowed_roles=['admin', 'mekaniku', 'nain'])
def dashboard(request):
    group = get_group(request.user)
    today = timezone.localdate()
    first = first_day_of_month(today)

    servisu = Servisu.objects.prefetch_related('items')
    if group == 'mekaniku':
        servisu = servisu.filter(mekanik=get_emp(request.user))

    low_qs = Pesa.objects.filter(is_active=True, stock__lte=F('stock_min'))
    show_finance = group in ('admin', 'nain')

    status_counts = {label: servisu.filter(status=key).count() for key, label in Servisu.STATUS_CHOICES}
    months, revenue, profit = [], [], []
    if show_finance:
        for back in range(5, -1, -1):
            start, end = month_start(today, back), month_start(today, back - 1)
            done = Servisu.objects.filter(status=Servisu.REMATA, date__gte=start, date__lt=end) \
                .prefetch_related('items')
            rev = lusru = Decimal('0')
            for s in done:
                rev += s.total
                lusru += s.profit
            desp = Despeza.objects.filter(date__gte=start, date__lt=end).aggregate(t=Sum('amount'))['t'] or 0
            months.append(start.strftime('%m/%Y'))
            revenue.append(float(rev))
            profit.append(float(lusru - desp))

    top = (ServisuPesa.objects.values('pesa__name').annotate(q=Sum('quantity')).order_by('-q')[:5])
    context = {
        'show_finance': show_finance,
        'n_pesa': Pesa.objects.filter(is_active=True).count(),
        'n_stock_low': low_qs.count(),
        'low_items': low_qs.order_by('stock')[:8],
        'n_servisu_fulan': servisu.filter(date__gte=first).count(),
        'n_servisu_pendente': servisu.exclude(status=Servisu.REMATA).count(),
        'recent': servisu.select_related('kliente', 'motor', 'mekanik').order_by('-date', '-id')[:6],
        'stock_value': sum((p.stock_value for p in Pesa.objects.filter(is_active=True)), Decimal('0')),
        'revenue_month': revenue[-1] if revenue else 0,
        'chart_data': {
            'months': months, 'revenue': revenue, 'profit': profit,
            'status_labels': list(status_counts.keys()), 'status_values': list(status_counts.values()),
            'top_labels': [t['pesa__name'][:28] for t in top], 'top_values': [t['q'] for t in top],
        },
        'title': 'Dashboard',
        'legend': 'Dashboard',
        'link_antes': [{'link_name': "dashboard", 'link_text': "Dashboard"}],
    }
    return render(request, 'report/dashboard.html', context)
