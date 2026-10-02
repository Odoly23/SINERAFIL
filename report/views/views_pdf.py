from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from config.decorators import allowed_users
from pesa.models import MovimentuStock, Pesa
from report import pdf
from report.forms import ReportForm
from servisu.models import Despeza, Servisu
from servisu.utils import can_view_servisu


def pdf_response(content, filename, download=False):
    resp = HttpResponse(content, content_type='application/pdf')
    resp['Content-Disposition'] = '%s; filename="%s"' % ('attachment' if download else 'inline', filename)
    return resp


@login_required
@allowed_users(allowed_roles=['admin', 'nain'])
def relatoriu(request):
    context = {
        'title': 'Relatóriu PDF',
        'legend': 'Relatóriu PDF',
        'link_antes': [{'link_name': "relatoriu", 'link_text': "Relatóriu PDF"}],
    }
    if not request.GET.get('tipu'):
        context['form'] = ReportForm()
        return render(request, 'report/index.html', context)
    form = ReportForm(request.GET)
    if not form.is_valid():
        context['form'] = form
        return render(request, 'report/index.html', context)
    d = form.cleaned_data
    d1, d2 = d['date_from'], d['date_to']
    download = bool(request.GET.get('download'))
    if d['tipu'] == 'stock':
        qs = Pesa.objects.filter(is_active=True).select_related('kategoria').order_by('name')
        return pdf_response(pdf.stock_report(qs), 'relatoriu-stock.pdf', download)
    if d['tipu'] == 'movimentu':
        qs = MovimentuStock.objects.filter(date__range=(d1, d2)).select_related('pesa').order_by('date', 'id')
        label = 'Tama no Sai'
        if d['movimentu']:
            qs = qs.filter(tipu=d['movimentu'])
            label = dict(MovimentuStock.TIPU_CHOICES)[d['movimentu']]
        return pdf_response(pdf.movimentu_report(qs, d1, d2, label), 'relatoriu-movimentu.pdf', download)
    servisu = (Servisu.objects.filter(status=Servisu.REMATA, date__range=(d1, d2))
               .select_related('kliente', 'motor', 'mekanik').prefetch_related('items').order_by('date', 'id'))
    despeza = Despeza.objects.filter(date__range=(d1, d2)).order_by('date')
    return pdf_response(pdf.finance_report(servisu, despeza, d1, d2), 'relatoriu-finanseiru.pdf', download)


@login_required
@allowed_users(allowed_roles=['admin', 'mekaniku', 'nain'])
def nota_servisu(request, pk):
    s = get_object_or_404(Servisu.objects.select_related('kliente', 'motor', 'mekanik'), pk=pk)
    if not can_view_servisu(request.user, s):
        return render(request, 'auth/404.html', status=403)
    return pdf_response(pdf.nota_servisu(s), 'nota-%s.pdf' % s.invoice_no, bool(request.GET.get('download')))
