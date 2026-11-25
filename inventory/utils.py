from django.db import transaction

from inventory.models import Part, StockMovement


class StockError(Exception):
    pass


@transaction.atomic
def register_movement(part, movement_type, quantity, note=''):
    """Update Stock Quantity: rejistu movimentu tama/sai no atualiza stock pesa. Stock labele negativu."""
    part = Part.objects.select_for_update().get(pk=getattr(part, 'pk', part))
    if quantity <= 0:
        raise StockError('Kuantidade tenke boot liu 0.')
    if movement_type == StockMovement.OUT:
        if part.stock < quantity:
            raise StockError('Stock "%s" la to\'o (iha %s, presiza %s).' % (part.name, part.stock, quantity))
        part.stock -= quantity
    else:
        part.stock += quantity
    part.save(update_fields=['stock'])
    return StockMovement.objects.create(part=part, movement_type=movement_type, quantity=quantity,
                                        note=(note or '')[:200])
