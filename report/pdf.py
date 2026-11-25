"""Konstrutór PDF ho ReportLab (relatóriu stock, movimentu, finanseiru no nota servisu)."""
from decimal import Decimal
from io import BytesIO

from django.conf import settings
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A5, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import HRFlowable, Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

BLOOD = colors.HexColor('#8b0000')
MAROON = colors.HexColor('#5c0a14')
LIGHT = colors.HexColor('#f8ecec')
GRID = colors.HexColor('#d8b8b8')

styles = getSampleStyleSheet()
S_TITLE = ParagraphStyle('t', parent=styles['Title'], textColor=MAROON, fontSize=16, spaceAfter=2)
S_SUB = ParagraphStyle('s', parent=styles['Normal'], textColor=colors.grey, fontSize=9, alignment=1)
S_H = ParagraphStyle('h', parent=styles['Heading3'], textColor=BLOOD, spaceBefore=8, spaceAfter=4)
S_N = ParagraphStyle('n', parent=styles['Normal'], fontSize=9)
S_CELL = ParagraphStyle('c', parent=styles['Normal'], fontSize=8, leading=10)


def usd(v):
    return '$ {:,.2f}'.format(Decimal(v or 0))


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(doc.leftMargin, 1 * cm, '%s — %s' % (
        settings.SHOP_NAME, timezone.localtime().strftime('%d/%m/%Y %H:%M')))
    canvas.drawRightString(doc.pagesize[0] - doc.rightMargin, 1 * cm, 'Pájina %d' % doc.page)
    canvas.restoreState()


LOGO = str(settings.BASE_DIR / 'main' / 'static' / 'Image' / 'logo.png')


def _brand():
    """Kop: logo iha karuk, naran ofisina no kontaktu iha klaran."""
    text = [Paragraph(settings.SHOP_NAME.upper(), S_TITLE),
            Paragraph('%s · %s · %s' % (settings.SHOP_TAGLINE, settings.SHOP_ADDRESS, settings.SHOP_PHONE), S_SUB)]
    t = Table([[Image(LOGO, width=1.8 * cm, height=1.8 * cm), text]], colWidths=[2.2 * cm, None])
    t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('LEFTPADDING', (0, 0), (-1, -1), 0)]))
    return t


def _header(title, subtitle=''):
    out = [
        _brand(),
        Spacer(1, 6),
        HRFlowable(width='100%', thickness=2, color=BLOOD),
        Spacer(1, 8),
        Paragraph('<b>%s</b>' % title, ParagraphStyle('tt', parent=styles['Heading2'], textColor=MAROON, spaceAfter=2)),
    ]
    if subtitle:
        out.append(Paragraph(subtitle, S_N))
    out.append(Spacer(1, 8))
    return out


def _table(data, widths, align_right=(), total_row=False, font=8):
    t = Table(data, colWidths=widths, repeatRows=1)
    st = [
        ('BACKGROUND', (0, 0), (-1, 0), MAROON),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), font),
        ('GRID', (0, 0), (-1, -1), 0.3, GRID),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]
    for c in align_right:
        st.append(('ALIGN', (c, 0), (c, -1), 'RIGHT'))
    if total_row:
        st += [('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
               ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecd0d0'))]
    t.setStyle(TableStyle(st))
    return t


def _render(story, pagesize=A4, margins=1.5 * cm):
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=pagesize, leftMargin=margins, rightMargin=margins,
                            topMargin=margins, bottomMargin=1.8 * cm, title=settings.SHOP_NAME)
    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buf.getvalue()


def stock_report(parts):
    rows = [['Nu', 'SKU', 'Naran pesa', 'Kategoria', 'Supplier', 'Stock', 'Mínimu', 'Folin sosa', 'Valór stock']]
    total = Decimal('0')
    low = 0
    for i, p in enumerate(parts, 1):
        rows.append([i, p.sku, Paragraph(p.name, S_CELL), str(p.category or '—'), Paragraph(str(p.supplier or '—'), S_CELL),
                     ('%s *' % p.stock) if p.is_low else p.stock, p.minimum_stock,
                     usd(p.purchase_price), usd(p.stock_value)])
        total += p.stock_value
        low += p.is_low
    rows.append(['', '', 'TOTÁL', '', '', '', '', '', usd(total)])
    story = _header('Relatóriu Stock Pesa-Rezerva',
                    'Data: %s · Pesa ho stock mínimu (*): <b>%d</b>' % (timezone.localdate().strftime('%d/%m/%Y'), low))
    story.append(_table(rows, [0.8 * cm, 2 * cm, 4.8 * cm, 2 * cm, 2.2 * cm, 1.2 * cm, 1.2 * cm, 1.7 * cm, 2 * cm],
                        align_right=(5, 6, 7, 8), total_row=True, font=7))
    return _render(story)


def movement_report(qs, d1, d2, label):
    rows = [['Data', 'Pesa', 'Tipu', 'Kuant.', 'Nota']]
    t_in = t_out = 0
    for m in qs:
        rows.append([timezone.localtime(m.created_at).strftime('%d/%m/%Y %H:%M'), Paragraph(m.part.name, S_CELL),
                     'Tama (In)' if m.movement_type == 'in' else 'Sai (Out)', m.quantity,
                     Paragraph(m.note or '—', S_CELL)])
        if m.movement_type == 'in':
            t_in += m.quantity
        else:
            t_out += m.quantity
    story = _header('Relatóriu Stock Tama no Sai',
                    'Períodu: %s – %s · Tipu: %s' % (d1.strftime('%d/%m/%Y'), d2.strftime('%d/%m/%Y'), label))
    story.append(_table(rows, [3 * cm, 6.5 * cm, 2.2 * cm, 1.5 * cm, 5 * cm], align_right=(3,)))
    story += [Spacer(1, 8), Paragraph('Total unidade tama: <b>%d</b> · Total unidade sai: <b>%d</b>' % (t_in, t_out), S_N)]
    return _render(story)


def repair_report(repairs, d1, d2):
    """Relatóriu reparasaun (finanseiru): reparasaun ho status Remata iha períodu."""
    rows = [['Nú. Reparasaun', 'Data', 'Kliente', 'Ekipamentu', 'Mekániku', 'Pesa', 'Servisu', 'Total']]
    t_parts = t_service = t_profit = Decimal('0')
    repairs = list(repairs)
    for r in repairs:
        rows.append([r.repair_number, timezone.localtime(r.created_at).strftime('%d/%m/%y'),
                     Paragraph(r.customer.name, S_CELL), Paragraph(r.equipment.name, S_CELL),
                     r.technician.display_name if r.technician else '—',
                     usd(r.parts_total), usd(r.service_cost), usd(r.total)])
        t_parts += r.parts_total
        t_service += r.service_cost
        t_profit += r.profit
    rows.append(['', '', '', '', 'TOTÁL', usd(t_parts), usd(t_service), usd(t_parts + t_service)])
    story = _header('Relatóriu Reparasaun (Finanseiru)',
                    'Períodu: %s – %s · Reparasaun ho status <b>Remata</b>: %d' % (
                        d1.strftime('%d/%m/%Y'), d2.strftime('%d/%m/%Y'), len(repairs)))
    story.append(_table(rows, [2.9 * cm, 1.6 * cm, 3 * cm, 3 * cm, 2.2 * cm, 1.8 * cm, 1.8 * cm, 1.9 * cm],
                        align_right=(5, 6, 7), total_row=True, font=7))
    story.append(Paragraph('Rezumu', S_H))
    summary = [
        ['Rendimentu pesa (unit_price x kuantidade)', usd(t_parts)],
        ['Rendimentu ongkos servisu', usd(t_service)],
        ['Rendimentu total', usd(t_parts + t_service)],
        ['Lukru estimadu (ongkos servisu + folin faan - folin sosa pesa)', usd(t_profit)],
    ]
    t = Table(summary, colWidths=[13 * cm, 4 * cm])
    t.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.3, GRID), ('FONTSIZE', (0, 0), (-1, -1), 9),
                           ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                           ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecd0d0')),
                           ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')]))
    story.append(t)
    return _render(story)


def repair_invoice(r):
    """Invoice/nota reparasaun (A5): kliente, ekipamentu, pesa uza, ongkos no total."""
    story = _header('Invoice Reparasaun %s' % r.repair_number)
    info = [
        ['Data', timezone.localtime(r.created_at).strftime('%d/%m/%Y'), 'Status', r.get_status_display()],
        ['Kliente', r.customer.name, 'Telefone', r.customer.phone or '—'],
        ['Ekipamentu', r.equipment.name, 'Plaka', r.equipment.plate or '—'],
        ['Mekániku', r.technician.display_name if r.technician else '—', 'Nu. Rangka', r.equipment.serial_number or '—'],
    ]
    t = Table(info, colWidths=[2 * cm, 4.5 * cm, 2 * cm, 3.5 * cm])
    t.setStyle(TableStyle([('FONTSIZE', (0, 0), (-1, -1), 8.5),
                           ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                           ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                           ('BOTTOMPADDING', (0, 0), (-1, -1), 2), ('TOPPADDING', (0, 0), (-1, -1), 2)]))
    story.append(t)
    if r.diagnosis:
        story += [Spacer(1, 4), Paragraph('<b>Diagnóstiku:</b> %s' % r.diagnosis, S_N)]
    story.append(Spacer(1, 6))
    rows = [['Nu', 'Pesa', 'Kuant.', 'Folin', 'Subtotal']]
    for i, it in enumerate(r.parts.select_related('part'), 1):
        rows.append([i, Paragraph(it.part.name, S_CELL), it.quantity, usd(it.unit_price), usd(it.subtotal)])
    if len(rows) == 1:
        rows.append(['', 'La uza pesa', '', '', ''])
    story.append(_table(rows, [0.8 * cm, 6.2 * cm, 1.3 * cm, 2 * cm, 2.2 * cm], align_right=(2, 3, 4)))
    story.append(Spacer(1, 6))
    tot = [['Total pesa', usd(r.parts_total)], ['Ongkos servisu', usd(r.service_cost)], ['TOTÁL', usd(r.total)]]
    tt = Table(tot, colWidths=[4 * cm, 3 * cm], hAlign='RIGHT')
    tt.setStyle(TableStyle([('ALIGN', (1, 0), (1, -1), 'RIGHT'), ('FONTSIZE', (0, 0), (-1, -1), 9),
                            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                            ('LINEABOVE', (0, -1), (-1, -1), 0.8, MAROON)]))
    story += [tt, Spacer(1, 18), Paragraph('Obrigadu ba konfiansa ba ita-nia ofisina.', S_SUB)]
    return _render(story, pagesize=A5, margins=1.2 * cm)
