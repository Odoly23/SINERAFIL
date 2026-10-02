from django.db import transaction

from pesa.models import MovimentuStock, Pesa


class StockError(Exception):
    pass


@transaction.atomic
def register_movement(pesa, tipu, quantity, user=None, **extra):
    """Rejistu movimentu stock (tama/sai) no atualiza stock pesa nian. Stock labele negativu."""
    pesa = Pesa.objects.select_for_update().get(pk=getattr(pesa, 'pk', pesa))
    if quantity <= 0:
        raise StockError('Kuantidade tenke boot liu 0.')
    if tipu == MovimentuStock.SAI:
        if pesa.stock < quantity:
            raise StockError(
                'Stock "%s" la to\'o (iha %s, presiza %s).' % (pesa.name, pesa.stock, quantity))
        pesa.stock -= quantity
    else:
        pesa.stock += quantity
    pesa.save(update_fields=['stock'])
    extra.setdefault('price', pesa.price_buy if tipu == MovimentuStock.TAMA else pesa.price_sell)
    return MovimentuStock.objects.create(pesa=pesa, tipu=tipu, quantity=quantity, created_by=user, **extra)
