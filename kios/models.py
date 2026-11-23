from decimal import Decimal

from django.db import models
from django.utils import timezone

from custom.models import BaseModel


class Faan(BaseModel):
    """Faan sasán (penjualan kios): sasán faan direta ba kliente, selu cash USD."""
    REMATA = 'remata'
    ANULADA = 'anulada'
    STATUS_CHOICES = [(REMATA, 'Remata'), (ANULADA, 'Anulada')]

    invoice_no = models.CharField(max_length=20, unique=True, editable=False, verbose_name='Nú. Invoice')
    date = models.DateTimeField(default=timezone.now, verbose_name='Data')
    kliente = models.ForeignKey('cliente.Kliente', null=True, blank=True, on_delete=models.SET_NULL,
                                related_name='faan', verbose_name='Kliente')
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Diskaun (USD)')
    paid = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Osan Selu (USD)')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=REMATA, verbose_name='Status')
    note = models.CharField(max_length=200, blank=True, verbose_name='Nota')

    class Meta:
        ordering = ['-date', '-id']
        verbose_name_plural = 'Faan Kios'

    def __str__(self):
        return self.invoice_no

    def save(self, *args, **kwargs):
        if not self.invoice_no:
            prefix = 'KIO-%s-' % timezone.localtime(self.date or timezone.now()).strftime('%Y%m')
            last = (Faan.objects.filter(invoice_no__startswith=prefix)
                    .order_by('-invoice_no').values_list('invoice_no', flat=True).first())
            n = int(last.split('-')[-1]) + 1 if last else 1
            self.invoice_no = '%s%04d' % (prefix, n)
        super().save(*args, **kwargs)

    @property
    def subtotal(self):
        return sum((i.subtotal for i in self.items.all()), Decimal('0'))

    @property
    def total(self):
        return max(self.subtotal - self.discount, Decimal('0'))

    @property
    def change(self):
        """Osan fila (troco) ba kliente."""
        return max(self.paid - self.total, Decimal('0'))

    @property
    def profit(self):
        gross = sum(((i.price_sell - i.price_buy) * i.quantity for i in self.items.all()), Decimal('0'))
        return gross - self.discount

    @property
    def n_items(self):
        return sum(i.quantity for i in self.items.all())


class FaanItem(models.Model):
    faan = models.ForeignKey(Faan, on_delete=models.CASCADE, related_name='items')
    pesa = models.ForeignKey('pesa.Pesa', on_delete=models.PROTECT, related_name='faan_items')
    quantity = models.PositiveIntegerField(verbose_name='Kuantidade')
    price_buy = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    price_sell = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Folin')

    def __str__(self):
        return '%s x%s' % (self.pesa.name, self.quantity)

    @property
    def subtotal(self):
        return self.quantity * self.price_sell
