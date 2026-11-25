from decimal import Decimal

from django.db import models

from custom.models import Category, Supplier


class Part(models.Model):
    """Tabel PART (ERD): id, sku, name, category_id, supplier_id, stock, minimum_stock, purchase_price.
    Kolun tambahan: selling_price (folin faan, default ba unit_price iha REPAIR_PART)."""
    sku = models.CharField(max_length=40, unique=True, verbose_name='SKU')
    name = models.CharField(max_length=200, verbose_name='Naran Pesa')
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL,
                                 related_name='parts', verbose_name='Kategoria')
    supplier = models.ForeignKey(Supplier, null=True, blank=True, on_delete=models.SET_NULL,
                                 related_name='parts', verbose_name='Supplier')
    stock = models.IntegerField(default=0, editable=False, verbose_name='Stock')
    minimum_stock = models.PositiveIntegerField(default=3, verbose_name='Stock Mínimu')
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Folin Sosa (USD)')
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Folin Faan (USD)')  # tambahan

    class Meta:
        db_table = 'part'
        ordering = ['name']
        verbose_name_plural = 'Part'

    def __str__(self):
        return '%s — %s' % (self.sku, self.name)

    @property
    def is_low(self):
        return self.stock <= self.minimum_stock

    @property
    def stock_value(self):
        return self.stock * self.purchase_price

    @property
    def margin(self):
        return self.selling_price - self.purchase_price


class StockMovement(models.Model):
    """Tabel STOCK_MOVEMENT (ERD): id, part_id, movement_type, quantity, created_at.
    Kolun tambahan: note (razaun/referénsia movimentu)."""
    IN = 'in'
    OUT = 'out'
    TYPE_CHOICES = [(IN, 'Tama (In)'), (OUT, 'Sai (Out)')]

    part = models.ForeignKey(Part, on_delete=models.PROTECT, related_name='movements', verbose_name='Pesa')
    movement_type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name='Tipu')
    quantity = models.PositiveIntegerField(verbose_name='Kuantidade')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Data/Oras')
    note = models.CharField(max_length=200, blank=True, verbose_name='Nota')   # tambahan

    class Meta:
        db_table = 'stock_movement'
        ordering = ['-created_at', '-id']
        verbose_name_plural = 'Stock Movement'

    def __str__(self):
        return '%s %s x%s' % (self.movement_type, self.part.name, self.quantity)
