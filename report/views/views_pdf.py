from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from config.activity import log_activity
from config.decorators import allowed_users
from inventory.models import Part, StockMovement
from repairs.models import Repair
from repairs.utils import can_view
from report import pdf
from report.forms import ReportForm


def pdf_response(content, filename, download=False):
    resp = HttpResponse(content, content_type='application/pdf')
    resp['Content-Disposition'] = '%s; filename="%s"' % ('attachment' if download else 'inline', filename)
    return resp


@login_required
@allowed_users(allowed_roles=['admin', 'owner'])
def reports(request):
    """Reports: stock, movimentu stock no reparasaun (PDF)."""
    context = {
        'title': 'Relatóriu PDF',
        'legend': 'Relatóriu PDF (Reports)',
        'link_antes': [{'link_name': "reports", 'link_text': "Reports"}],
    }
    if not request.GET.get('type'):
        context['form'] = ReportForm()
        return render(request, 'report/index.html', context)
    form = ReportForm(request.GET)
    if not form.is_valid():
        context['form'] = form
        return render(request, 'report/index.html', context)
    d = form.cleaned_data
    d1, d2 = d['date_from'], d['date_to']
    download = bool(request.GET.get('download'))
    log_activity(request.user, 'Relatóriu %s' % d['type'])
    if d['type'] == 'stock':
        qs = Part.objects.select_related('category', 'supplier').order_by('name')
        return pdf_response(pdf.stock_report(qs), 'relatoriu-stock.pdf', download)
    if d['type'] == 'movement':
        qs = (StockMovement.objects.filter(created_at__date__range=(d1, d2))
              .select_related('part').order_by('created_at', 'id'))
        label = 'Tama no Sai'
        if d['movement']:
            qs = qs.filter(movement_type=d['movement'])
            label = dict(StockMovement.TYPE_CHOICES)[d['movement']]
        return pdf_response(pdf.movement_report(qs, d1, d2, label), 'relatoriu-movimentu.pdf', download)
    repairs = (Repair.objects.filter(status=Repair.COMPLETED, created_at__date__range=(d1, d2))
               .select_related('customer', 'equipment', 'technician').prefetch_related('parts__part')
               .order_by('created_at', 'id'))
    return pdf_response(pdf.repair_report(repairs, d1, d2), 'relatoriu-reparasaun.pdf', download)


@login_required
@allowed_users(allowed_roles=['admin', 'technician', 'owner'])
def repair_invoice(request, pk):
    r = get_object_or_404(Repair.objects.select_related('customer', 'equipment', 'technician'), pk=pk)
    if not can_view(request.user, r):
        return render(request, 'auth/404.html', status=403)
    return pdf_response(pdf.repair_invoice(r), 'invoice-%s.pdf' % r.repair_number, bool(request.GET.get('download')))
