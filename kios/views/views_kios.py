from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from cliente.models import Kliente
from config.decorators import allowed_users
from kios.models import Faan
from kios.utils import SaleError, create_sale, find_pesa, void_sale
from pesa.models import Pesa
from report import pdf

LINK = [{'link_name': "kios", 'link_text': "Kios"}]
ADMIN = ['admin']


def pesa_json(p):
    return {'id': p.pk, 'code': p.code, 'barcode': p.barcode or '', 'name': p.name,
            'price': str(p.price_sell), 'stock': p.stock, 'unit': p.unit}


@login_required
@allowed_users(allowed_roles=ADMIN)
def kios(request):
    context = {
        'kliente_list': Kliente.objects.all(),
        'title': 'Kios — Faan Sasán',
        'legend': 'Kios — Faan Sasán',
        'link_antes': LINK,
        'pos': True,
    }
    return render(request, 'kios/kios.html', context)


@login_required
@allowed_users(allowed_roles=ADMIN)
@require_GET
def kios_scan(request):
    """Scanner barcode/kódigu -> JSON pesa."""
    p = find_pesa(request.GET.get('q'))
    if not p:
        return JsonResponse({'error': 'Kódigu "%s" la hetan.' % request.GET.get('q', '').strip()}, status=404)
    return JsonResponse(pesa_json(p))


@login_required
@allowed_users(allowed_roles=ADMIN)
@require_GET
def kios_cari(request):
    """Buka pesa tuir naran/kódigu (ba sasán ne'ebé la iha barcode)."""
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})
    qs = (Pesa.objects.filter(is_active=True, name__icontains=q)
          | Pesa.objects.filter(is_active=True, code__icontains=q)).distinct().order_by('name')[:12]
    return JsonResponse({'results': [pesa_json(p) for p in qs]})


@login_required
@allowed_users(allowed_roles=ADMIN)
@require_POST
def kios_checkout(request):
    kliente = None
    if request.POST.get('kliente'):
        kliente = Kliente.objects.filter(pk=request.POST['kliente']).first()
    try:
        faan = create_sale(request.user, request.POST.get('cart'), request.POST.get('discount'),
                           request.POST.get('paid'), kliente=kliente, note=request.POST.get('note', ''))
    except SaleError as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)
    return JsonResponse({
        'ok': True, 'invoice': faan.invoice_no, 'total': str(faan.total), 'change': str(faan.change),
        'detail_url': reverse('faan-detail', args=[faan.pk]),
        'struk_url': reverse('faan-struk', args=[faan.pk]) + '?auto=1',
    })


@login_required
@allowed_users(allowed_roles=ADMIN)
def faan_list(request):
    objects = Faan.objects.select_related('kliente', 'created_by').prefetch_related('items')
    status = request.GET.get('status', '')
    if status in dict(Faan.STATUS_CHOICES):
        objects = objects.filter(status=status)
    context = {
        'objects': objects[:1000],
        'status': status,
        'title': 'Istória Faan Kios',
        'legend': 'Istória Faan Kios',
        'link_antes': LINK + [{'link_name': "faan-list", 'link_text': "Istória Faan"}],
    }
    return render(request, 'kios/list.html', context)


@login_required
@allowed_users(allowed_roles=ADMIN)
def faan_detail(request, pk):
    obj = get_object_or_404(Faan.objects.select_related('kliente', 'created_by').prefetch_related('items__pesa'), pk=pk)
    context = {
        'obj': obj,
        'title': 'Faan %s' % obj.invoice_no,
        'legend': 'Faan %s' % obj.invoice_no,
        'link_antes': LINK + [{'link_name': "faan-list", 'link_text': "Istória Faan"}],
    }
    return render(request, 'kios/detail.html', context)


@login_required
@allowed_users(allowed_roles=ADMIN)
def faan_struk(request, pk):
    """Struk 80mm (printer thermal) — pájina HTML ho @page 80mm."""
    obj = get_object_or_404(Faan.objects.select_related('kliente', 'created_by').prefetch_related('items__pesa'), pk=pk)
    return render(request, 'kios/struk.html', {'obj': obj, 'auto': bool(request.GET.get('auto'))})


@login_required
@allowed_users(allowed_roles=ADMIN)
def faan_pdf(request, pk):
    from report.views.views_pdf import pdf_response
    obj = get_object_or_404(Faan.objects.select_related('kliente', 'created_by').prefetch_related('items__pesa'), pk=pk)
    return pdf_response(pdf.faan_invoice(obj), 'invoice-%s.pdf' % obj.invoice_no, bool(request.GET.get('download')))


@login_required
@allowed_users(allowed_roles=ADMIN)
@require_POST
def faan_void(request, pk):
    obj = get_object_or_404(Faan, pk=pk)
    try:
        void_sale(obj, request.user)
        messages.success(request, 'Faan %s anula ona; stock fila fali.' % obj.invoice_no)
    except SaleError as e:
        messages.error(request, str(e))
    return redirect('faan-detail', pk=pk)
