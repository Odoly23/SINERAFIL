from config.auth_utils import get_emp, get_group
from pesa.models import MovimentuStock
from pesa.utils import register_movement
from servisu.models import Servisu


def can_edit_servisu(user, servisu):
    """Admin: sempre; mekániku: servisu rasik nian ne'ebé seidauk remata."""
    group = get_group(user)
    if group == 'admin':
        return True
    if group == 'mekaniku':
        emp = get_emp(user)
        return emp is not None and servisu.mekanik_id == emp.pk and servisu.status != Servisu.REMATA
    return False


def can_view_servisu(user, servisu):
    group = get_group(user)
    if group in ('admin', 'nain'):
        return True
    if group == 'mekaniku':
        emp = get_emp(user)
        return emp is not None and servisu.mekanik_id == emp.pk
    return False


def restore_items(servisu, user):
    """Fila stock ba pesa hotu-hotu ne'ebé uza iha servisu."""
    for item in servisu.items.select_related('pesa'):
        register_movement(
            item.pesa, MovimentuStock.TAMA, item.quantity, user=user,
            price=item.price_buy, reference=servisu.invoice_no,
            note='Retorna husi servisu %s' % servisu.invoice_no)
