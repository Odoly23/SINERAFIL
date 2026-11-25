from django.db import transaction

from config.auth_utils import get_role
from inventory.models import StockMovement
from inventory.utils import StockError, register_movement
from repairs.models import Repair, RepairPart


class RepairError(Exception):
    pass


def can_view(user, repair):
    role = get_role(user)
    if role in ('admin', 'owner'):
        return True
    return role == 'technician' and repair.technician_id == user.pk


def can_operate(user, repair):
    """Admin: sempre (se seidauk remata). Mekániku: de'it reparasaun ne'ebé hili ba nia."""
    if repair.status == Repair.COMPLETED:
        return False
    role = get_role(user)
    if role == 'admin':
        return True
    return role == 'technician' and repair.technician_id == user.pk


def workflow_steps(repair):
    """Etapa tuir flowchart: Register -> Diagnosis -> Assign -> Spare Parts -> Repair Process -> Completion."""
    idx = repair.status_index
    defs = [
        ('Register New Repair', 'Rejistu Reparasaun Foun', 'fa-clipboard-list', 0),
        ('Damage Diagnosis', 'Diagnóstiku Estragu', 'fa-search', 1),
        ('Assign Technician', 'Hili Mekániku', 'fa-user-cog', 2),
        ('Spare Parts Usage', 'Uza Pesa (stock redús automátiku)', 'fa-cogs', 3),
        ('Repair Process', 'Prosesu Reparasaun', 'fa-wrench', 4),
        ('Confirm Completion', 'Konfirma Remata', 'fa-check-circle', 4),
    ]
    steps, current_found = [], False
    for en, tet, icon, threshold in defs:
        done = idx >= threshold and not (threshold == 4 and idx < 4)
        if threshold == 0:
            done = True
        state = 'done' if done else ('current' if not current_found else 'todo')
        if state == 'current':
            current_found = True
        steps.append({'en': en, 'tet': tet, 'icon': icon, 'state': state})
    return steps


@transaction.atomic
def add_part(repair, part, quantity, unit_price=None):
    """Spare Parts Usage + Automatic Stock Update."""
    if repair.status not in (Repair.ASSIGNED, Repair.IN_PROGRESS):
        raise RepairError('Pesa bele uza de\'it depois mekániku hili no molok reparasaun remata.')
    register_movement(part, StockMovement.OUT, quantity, note='Uza iha reparasaun %s' % repair.repair_number)
    price = part.selling_price if unit_price in (None, '') else unit_price
    item = repair.parts.filter(part=part, unit_price=price).first()
    if item:
        item.quantity += quantity
        item.save()
    else:
        item = RepairPart.objects.create(repair=repair, part=part, quantity=quantity, unit_price=price)
    return item


@transaction.atomic
def remove_part(repair, item):
    register_movement(item.part, StockMovement.IN, item.quantity,
                      note='Hasai husi reparasaun %s' % repair.repair_number)
    item.delete()


@transaction.atomic
def restore_parts(repair):
    """Fila stock pesa hotu-hotu (bainhira reparasaun hamoos)."""
    for item in repair.parts.select_related('part'):
        register_movement(item.part, StockMovement.IN, item.quantity,
                          note='Retorna husi reparasaun %s' % repair.repair_number)
