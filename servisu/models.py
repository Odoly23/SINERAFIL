from decimal import Decimal

from django.db import models
from django.utils import timezone

from custom.models import BaseModel


class Servisu(BaseModel):
    PENDENTE = 'pendente'
    PROSESU = 'prosesu'
    REMATA = 'remata'
    STATUS_CHOICES = [(PENDENTE, 'Pendente'), (PROSESU, 'Prosesu'), (REMATA, 'Remata')]

    invoice_no = models.CharField(max_length=20, unique=True, editable=False, verbose_name='Nú. Nota')
    date = models.DateField(default=timezone.localdate, verbose_name='Data')
    kliente = models.ForeignKey('cliente.Kliente', on_delete=models.PROTECT, related_name='servisu',
                                verbose_name='Kliente')
    motor = models.ForeignKey('cliente.Motor', on_delete=models.PROTECT, related_name='servisu',
                              verbose_name='Motór')
    mekanik = models.ForeignKey('users.Emp', on_delete=models.PROTECT, related_name='servisu',
                                verbose_name='Mekániku')
    complaint = models.TextField(blank=True, verbose_name='Problema / Servisu')
    labor_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Ongkos Servisu (USD)')
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Diskaun (USD)')
    mech_percent = models.DecimalField(max_digits=5, decimal_places=2, default=10, verbose_name='Persen Mekániku (%)')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDENTE, verbose_name='Status')
    note = models.TextField(blank=True, verbose_name='Nota')

    class Meta:
        ordering = ['-date', '-id']
        verbose_name_plural = 'Servisu'

    def __str__(self):
        return self.invoice_no

    def save(self, *args, **kwargs):
        if not self.invoice_no:
            prefix = 'SRV-%s-' % (self.date or timezone.localdate()).strftime('%Y%m')
            last = (Servisu.objects.filter(invoice_no__startswith=prefix)
                    .order_by('-invoice_no').values_list('invoice_no', flat=True).first())
            n = int(last.split('-')[-1]) + 1 if last else 1
            self.invoice_no = '%s%04d' % (prefix, n)
        super().save(*args, **kwargs)

    # ---- kálkulu
    @property
    def total_parts(self):
        return sum((i.subtotal for i in self.items.all()), Decimal('0'))

    @property
    def total(self):
        return max(self.total_parts + self.labor_cost - self.discount, Decimal('0'))

    @property
    def mech_fee(self):
        return (self.labor_cost * self.mech_percent / Decimal('100')).quantize(Decimal('0.01'))

    @property
    def labor_net(self):
        return self.labor_cost - self.mech_fee

    @property
    def profit_parts(self):
        return sum(((i.price_sell - i.price_buy) * i.quantity for i in self.items.all()), Decimal('0'))

    @property
    def profit(self):
        """Lukru ofisina: lukru pesa + ongkos bersih - diskaun."""
        return self.profit_parts + self.labor_net - self.discount


class ServisuPesa(models.Model):
    servisu = models.ForeignKey(Servisu, on_delete=models.CASCADE, related_name='items')
    pesa = models.ForeignKey('pesa.Pesa', on_delete=models.PROTECT, related_name='servisu_items')
    quantity = models.PositiveIntegerField(verbose_name='Kuantidade')
    price_buy = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    price_sell = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Folin')

    def __str__(self):
        return '%s x%s' % (self.pesa.name, self.quantity)

    @property
    def subtotal(self):
        return self.quantity * self.price_sell


class Despeza(BaseModel):
    date = models.DateField(default=timezone.localdate, verbose_name='Data')
    description = models.CharField(max_length=200, verbose_name='Deskrisaun')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Valór (USD)')

    class Meta:
        ordering = ['-date', '-id']
        verbose_name_plural = 'Despeza'

    def __str__(self):
        return self.description
