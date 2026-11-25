from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from config.utils import next_number


class Repair(models.Model):
    """Tabel REPAIR (ERD): id, repair_number, customer_id, equipment_id, technician_id, status, service_cost.
    Kolun tambahan: diagnosis (etapa Damage Diagnosis) no created_at."""
    REGISTERED = 'registered'
    DIAGNOSED = 'diagnosed'
    ASSIGNED = 'assigned'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    STATUS_CHOICES = [
        (REGISTERED, 'Rejistu'),
        (DIAGNOSED, 'Diagnóstiku'),
        (ASSIGNED, 'Mekániku Hili'),
        (IN_PROGRESS, 'Prosesu'),
        (COMPLETED, 'Remata'),
    ]
    ORDER = [REGISTERED, DIAGNOSED, ASSIGNED, IN_PROGRESS, COMPLETED]

    repair_number = models.CharField(max_length=20, unique=True, editable=False, verbose_name='Nú. Reparasaun')
    customer = models.ForeignKey('customers.Customer', on_delete=models.PROTECT, related_name='repairs',
                                 verbose_name='Kliente')
    equipment = models.ForeignKey('customers.Equipment', on_delete=models.PROTECT, related_name='repairs',
                                  verbose_name='Ekipamentu')
    technician = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT,
                                   related_name='repairs', verbose_name='Mekániku')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=REGISTERED, verbose_name='Status')
    service_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Ongkos Servisu (USD)')
    diagnosis = models.TextField(blank=True, verbose_name='Diagnóstiku Estragu')            # tambahan
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Data Rejistu')    # tambahan

    class Meta:
        db_table = 'repair'
        ordering = ['-created_at', '-id']
        verbose_name_plural = 'Repair'

    def __str__(self):
        return self.repair_number

    def save(self, *args, **kwargs):
        if not self.repair_number:
            prefix = 'RPR-%s-' % timezone.localtime(self.created_at).strftime('%Y%m')
            self.repair_number = next_number(Repair, 'repair_number', prefix)
        super().save(*args, **kwargs)

    @property
    def status_index(self):
        return self.ORDER.index(self.status)

    @property
    def parts_total(self):
        return sum((p.subtotal for p in self.parts.all()), Decimal('0'))

    @property
    def total(self):
        return self.service_cost + self.parts_total

    @property
    def parts_profit(self):
        """Lukru estimadu husi pesa: (unit_price - purchase_price) x kuantidade."""
        return sum(((p.unit_price - p.part.purchase_price) * p.quantity for p in self.parts.all()), Decimal('0'))

    @property
    def profit(self):
        return self.service_cost + self.parts_profit


class RepairPart(models.Model):
    """Tabel REPAIR_PART (ERD): id, repair_id, part_id, quantity, unit_price."""
    repair = models.ForeignKey(Repair, on_delete=models.CASCADE, related_name='parts')
    part = models.ForeignKey('inventory.Part', on_delete=models.PROTECT, related_name='repair_parts')
    quantity = models.PositiveIntegerField(verbose_name='Kuantidade')
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Folin Unitáriu')

    class Meta:
        db_table = 'repair_part'

    def __str__(self):
        return '%s x%s' % (self.part.name, self.quantity)

    @property
    def subtotal(self):
        return self.quantity * self.unit_price
