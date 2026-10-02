from decimal import Decimal

from django.db import models
from django.utils import timezone

from custom.models import BaseModel, Kategoria


class Pesa(BaseModel):
    code = models.CharField(max_length=40, unique=True, verbose_name='Kódigu')
    name = models.CharField(max_length=200, verbose_name='Naran Pesa')
    kategoria = models.ForeignKey(Kategoria, null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name='pesa', verbose_name='Kategoria')
    unit = models.CharField(max_length=20, default='pcs', verbose_name='Unidade')
    price_buy = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Folin Sosa (USD)')
    price_sell = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Folin Faan (USD)')
    stock = models.IntegerField(default=0, editable=False, verbose_name='Stock')
    stock_min = models.PositiveIntegerField(default=3, verbose_name='Stock Mínimu')
    description = models.TextField(blank=True, verbose_name='Deskrisaun')
    is_active = models.BooleanField(default=True, verbose_name='Ativu')

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Pesa'

    def __str__(self):
        return '%s — %s' % (self.code, self.name)

    @property
    def is_low(self):
        return self.stock <= self.stock_min

    @property
    def stock_value(self):
        return self.stock * self.price_buy

    @property
    def profit(self):
        return self.price_sell - self.price_buy


class MovimentuStock(BaseModel):
    TAMA = 'tama'
    SAI = 'sai'
    TIPU_CHOICES = [(TAMA, 'Tama'), (SAI, 'Sai')]

    pesa = models.ForeignKey(Pesa, on_delete=models.PROTECT, related_name='movimentu', verbose_name='Pesa')
    tipu = models.CharField(max_length=4, choices=TIPU_CHOICES, verbose_name='Tipu')
    quantity = models.PositiveIntegerField(verbose_name='Kuantidade')
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Folin Unitáriu (USD)')
    date = models.DateField(default=timezone.localdate, verbose_name='Data')
    reference = models.CharField(max_length=120, blank=True, verbose_name='Referénsia / Fornesedór')
    note = models.TextField(blank=True, verbose_name='Nota')
    servisu = models.ForeignKey('servisu.Servisu', null=True, blank=True, on_delete=models.SET_NULL,
                                related_name='movimentu')

    class Meta:
        ordering = ['-date', '-id']
        verbose_name_plural = 'Movimentu Stock'

    def __str__(self):
        return '%s %s x%s' % (self.get_tipu_display(), self.pesa.name, self.quantity)

    @property
    def total(self):
        return Decimal(self.quantity) * self.price
