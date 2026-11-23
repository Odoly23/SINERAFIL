import json
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.db.models import Q

from kios.models import Faan, FaanItem
from pesa.models import MovimentuStock, Pesa
from pesa.utils import StockError, register_movement

CENT = Decimal('0.01')


class SaleError(Exception):
    pass


def find_pesa(code):
    """Buka pesa ativu husi barcode ka kódigu (scanner USB hatama kódigu + Enter)."""
    code = (code or '').strip()
    if not code:
        return None
    return Pesa.objects.filter(is_active=True).filter(Q(barcode=code) | Q(code__iexact=code)).first()


def money(value, field):
    try:
        d = Decimal(str(value if value not in (None, '') else '0')).quantize(CENT)
    except (InvalidOperation, ValueError):
        raise SaleError('%s la loos.' % field)
    if d < 0:
        raise SaleError('%s labele negativu.' % field)
    return d


@transaction.atomic
def create_sale(user, cart_json, discount, paid, kliente=None, note=''):
    """Kria faan husi karrinhu: valida folin/stock iha server, hamenus stock, kalkula troco."""
    try:
        cart = json.loads(cart_json or '[]')
    except ValueError:
        raise SaleError('Karrinhu la loos.')
    wanted = {}
    for row in cart:
        try:
            pk, qty = int(row['pesa']), int(row['qty'])
        except (KeyError, TypeError, ValueError):
            raise SaleError('Karrinhu la loos.')
        if qty <= 0:
            raise SaleError('Kuantidade tenke boot liu 0.')
        wanted[pk] = wanted.get(pk, 0) + qty
    if not wanted:
        raise SaleError('Karrinhu mamuk.')
    pesas = {p.pk: p for p in Pesa.objects.filter(pk__in=wanted, is_active=True)}
    if len(pesas) != len(wanted):
        raise SaleError('Iha pesa ne\'ebé la hetan ka la ativu.')

    discount, paid = money(discount, 'Diskaun'), money(paid, 'Osan selu')
    subtotal = sum((pesas[pk].price_sell * q for pk, q in wanted.items()), Decimal('0'))
    if discount > subtotal:
        raise SaleError('Diskaun labele boot liu total sasán.')
    total = subtotal - discount
    if paid < total:
        raise SaleError('Osan selu la to\'o (kuran $ %s).' % (total - paid))

    faan = Faan.objects.create(kliente=kliente, discount=discount, paid=paid, note=(note or '')[:200],
                               created_by=user)
    try:
        for pk, qty in wanted.items():
            p = pesas[pk]
            register_movement(p, MovimentuStock.SAI, qty, user=user, price=p.price_sell,
                              reference=faan.invoice_no, faan=faan,
                              note='Faan kios %s' % faan.invoice_no)
            FaanItem.objects.create(faan=faan, pesa=p, quantity=qty,
                                    price_buy=p.price_buy, price_sell=p.price_sell)
    except StockError as e:
        raise SaleError(str(e))
    return faan


@transaction.atomic
def void_sale(faan, user):
    """Anula faan: stock fila fali."""
    if faan.status == Faan.ANULADA:
        raise SaleError('Faan ne\'e anula ona.')
    for item in faan.items.select_related('pesa'):
        register_movement(item.pesa, MovimentuStock.TAMA, item.quantity, user=user,
                          price=item.price_buy, reference=faan.invoice_no, faan=faan,
                          note='Anula faan %s' % faan.invoice_no)
    faan.status = Faan.ANULADA
    faan.updated_by = user
    faan.save()
