from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.shortcuts import render
from django.utils import timezone

from config.auth_utils import get_role
from config.decorators import allowed_users
from config.utils import first_day_of_month, month_start
from inventory.models import Part
from repairs.models import Repair, RepairPart


@login_required
@allowed_users(allowed_roles=['admin', 'technician', 'owner'])
def dashboard(request):
    """Dashboard (flowchart: lori ba Inventory Management, Repair Management no Reports)."""
    role = get_role(request.user)
    today = timezone.localdate()
    first = first_day_of_month(today)

    repairs = Repair.objects.prefetch_related('parts__part')
    if role == 'technician':
        repairs = repairs.filter(technician=request.user)

    low_qs = Part.objects.filter(stock__lte=F('minimum_stock'))
    show_finance = role in ('admin', 'owner')

    status_counts = {label: repairs.filter(status=key).count() for key, label in Repair.STATUS_CHOICES}
    months, revenue, profit = [], [], []
    if show_finance:
        for back in range(5, -1, -1):
            start, end = month_start(today, back), month_start(today, back - 1)
            done = Repair.objects.filter(status=Repair.COMPLETED, created_at__date__gte=start,
                                         created_at__date__lt=end).prefetch_related('parts__part')
            rev = lusru = Decimal('0')
            for r in done:
                rev += r.total
                lusru += r.profit
            months.append(start.strftime('%m/%Y'))
            revenue.append(float(rev))
            profit.append(float(lusru))

    top = (RepairPart.objects.values('part__name').annotate(q=Sum('quantity')).order_by('-q')[:5])
    context = {
        'show_finance': show_finance,
        'n_parts': Part.objects.count(),
        'n_stock_low': low_qs.count(),
        'low_items': low_qs.order_by('stock')[:8],
        'n_repairs_month': repairs.filter(created_at__date__gte=first).count(),
        'n_repairs_open': repairs.exclude(status=Repair.COMPLETED).count(),
        'recent': repairs.select_related('customer', 'equipment', 'technician').order_by('-created_at', '-id')[:6],
        'stock_value': sum((p.stock_value for p in Part.objects.all()), Decimal('0')),
        'revenue_month': revenue[-1] if revenue else 0,
        'chart_data': {
            'months': months, 'revenue': revenue, 'profit': profit,
            'status_labels': list(status_counts.keys()), 'status_values': list(status_counts.values()),
            'top_labels': [t['part__name'][:28] for t in top], 'top_values': [t['q'] for t in top],
        },
        'title': 'Dashboard',
        'legend': 'Dashboard',
        'link_antes': [{'link_name': "dashboard", 'link_text': "Dashboard"}],
    }
    return render(request, 'report/dashboard.html', context)
