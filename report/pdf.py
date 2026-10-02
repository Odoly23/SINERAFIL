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


def stock_report(pesa_qs):
    rows = [['Nu', 'Kódigu', 'Naran pesa', 'Kategoria', 'Stock', 'Mínimu', 'Folin sosa', 'Valór stock']]
    total = Decimal('0')
    low = 0
    for i, p in enumerate(pesa_qs, 1):
        rows.append([i, p.code, Paragraph(p.name, S_CELL), str(p.kategoria or '—'),
                     ('%s *' % p.stock) if p.is_low else p.stock, p.stock_min,
                     usd(p.price_buy), usd(p.stock_value)])
        total += p.stock_value
        low += p.is_low
    rows.append(['', '', 'TOTÁL', '', '', '', '', usd(total)])
    story = _header('Relatóriu Stock Pesa-Rezerva',
                    'Data: %s · Pesa ho stock mínimu: <b>%d</b>' % (timezone.localdate().strftime('%d/%m/%Y'), low))
    story.append(_table(rows, [0.9 * cm, 2.4 * cm, 6 * cm, 2.4 * cm, 1.4 * cm, 1.4 * cm, 2 * cm, 2.4 * cm],
                        align_right=(4, 5, 6, 7), total_row=True))
    return _render(story)


def movimentu_report(qs, d1, d2, tipu_label):
    rows = [['Data', 'Pesa', 'Tipu', 'Kuant.', 'Folin', 'Total', 'Referénsia']]
    t_tama = t_sai = Decimal('0')
    for m in qs:
        rows.append([m.date.strftime('%d/%m/%Y'), Paragraph(m.pesa.name, S_CELL), m.get_tipu_display(),
                     m.quantity, usd(m.price), usd(m.total), Paragraph(m.reference or '—', S_CELL)])
        if m.tipu == 'tama':
            t_tama += m.total
        else:
            t_sai += m.total
    story = _header('Relatóriu Sasán Tama no Sai',
                    'Períodu: %s – %s · Tipu: %s' % (d1.strftime('%d/%m/%Y'), d2.strftime('%d/%m/%Y'), tipu_label))
    story.append(_table(rows, [2 * cm, 6 * cm, 1.5 * cm, 1.5 * cm, 2 * cm, 2.3 * cm, 3 * cm], align_right=(3, 4, 5)))
    story += [Spacer(1, 8), Paragraph('Total tama: <b>%s</b> · Total sai: <b>%s</b>' % (usd(t_tama), usd(t_sai)), S_N)]
    return _render(story)


def finance_report(servisu_qs, despeza_qs, d1, d2):
    rows = [['Nota', 'Data', 'Kliente', 'Motór', 'Mekániku', 'Pesa', 'Ongkos', 'Diskaun', 'Total']]
    t_pesa = t_ongkos = t_diskon = t_total = t_lusru = t_mek = Decimal('0')
    for s in servisu_qs:
        rows.append([s.invoice_no, s.date.strftime('%d/%m/%y'), Paragraph(s.kliente.name, S_CELL), s.motor.plate,
                     s.mekanik.name, usd(s.total_parts), usd(s.labor_cost), usd(s.discount), usd(s.total)])
        t_pesa += s.total_parts
        t_ongkos += s.labor_cost
        t_diskon += s.discount
        t_total += s.total
        t_lusru += s.profit
        t_mek += s.mech_fee
    rows.append(['', '', '', '', 'TOTÁL', usd(t_pesa), usd(t_ongkos), usd(t_diskon), usd(t_total)])
    t_desp = sum((d.amount for d in despeza_qs), Decimal('0'))
    story = _header('Relatóriu Finanseiru Servisu',
                    'Períodu: %s – %s · Servisu ho status <b>Remata</b>' % (
                        d1.strftime('%d/%m/%Y'), d2.strftime('%d/%m/%Y')))
    story.append(_table(rows, [2.7 * cm, 1.6 * cm, 3 * cm, 2 * cm, 2 * cm, 1.9 * cm, 1.8 * cm, 1.6 * cm, 1.9 * cm],
                        align_right=(5, 6, 7, 8), total_row=True, font=7))
    story.append(Paragraph('Rezumu', S_H))
    summary = [
        ['Rendimentu total (servisu remata)', usd(t_total)],
        ['Ongkos mekániku (porsentu)', usd(t_mek)],
        ['Lukru servisu (pesa + ongkos bersih - diskaun)', usd(t_lusru)],
        ['Despeza ofisina iha períodu', usd(t_desp)],
        ['Lukru líkidu (lukru servisu - despeza)', usd(t_lusru - t_desp)],
    ]
    t = Table(summary, colWidths=[11 * cm, 4 * cm])
    t.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.3, GRID), ('FONTSIZE', (0, 0), (-1, -1), 9),
                           ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                           ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecd0d0')),
                           ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')]))
    story.append(t)
    if despeza_qs:
        story.append(Paragraph('Despeza', S_H))
        rows2 = [['Data', 'Deskrisaun', 'Valór']] + [
            [d.date.strftime('%d/%m/%Y'), Paragraph(d.description, S_CELL), usd(d.amount)] for d in despeza_qs]
        story.append(_table(rows2, [3 * cm, 11 * cm, 3 * cm], align_right=(2,)))
    return _render(story)


def nota_servisu(s):
    story = _header('Nota Servisu %s' % s.invoice_no)
    info = [
        ['Data', s.date.strftime('%d/%m/%Y'), 'Status', s.get_status_display()],
        ['Kliente', s.kliente.name, 'Telefone', s.kliente.phone or '—'],
        ['Motór', '%s %s' % (s.motor.brand, s.motor.model_name), 'Plaka', s.motor.plate],
        ['Mekániku', s.mekanik.name, '', ''],
    ]
    t = Table(info, colWidths=[2 * cm, 4.5 * cm, 2 * cm, 3.5 * cm])
    t.setStyle(TableStyle([('FONTSIZE', (0, 0), (-1, -1), 8.5),
                           ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                           ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                           ('BOTTOMPADDING', (0, 0), (-1, -1), 2), ('TOPPADDING', (0, 0), (-1, -1), 2)]))
    story.append(t)
    if s.complaint:
        story += [Spacer(1, 4), Paragraph('<b>Servisu / problema:</b> %s' % s.complaint, S_N)]
    story.append(Spacer(1, 6))
    rows = [['Nu', 'Pesa', 'Kuant.', 'Folin', 'Subtotal']]
    for i, it in enumerate(s.items.select_related('pesa'), 1):
        rows.append([i, Paragraph(it.pesa.name, S_CELL), it.quantity, usd(it.price_sell), usd(it.subtotal)])
    if len(rows) == 1:
        rows.append(['', 'La uza pesa', '', '', ''])
    story.append(_table(rows, [0.8 * cm, 6.2 * cm, 1.3 * cm, 2 * cm, 2.2 * cm], align_right=(2, 3, 4)))
    story.append(Spacer(1, 6))
    tot = [['Total pesa', usd(s.total_parts)], ['Ongkos servisu', usd(s.labor_cost)]]
    if s.discount:
        tot.append(['Diskaun', '- ' + usd(s.discount)])
    tot.append(['TOTÁL', usd(s.total)])
    tt = Table(tot, colWidths=[4 * cm, 3 * cm], hAlign='RIGHT')
    tt.setStyle(TableStyle([('ALIGN', (1, 0), (1, -1), 'RIGHT'), ('FONTSIZE', (0, 0), (-1, -1), 9),
                            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                            ('LINEABOVE', (0, -1), (-1, -1), 0.8, MAROON)]))
    story += [tt, Spacer(1, 18), Paragraph('Obrigadu ba konfiansa ba ita-nia ofisina.', S_SUB)]
    return _render(story, pagesize=A5, margins=1.2 * cm)
