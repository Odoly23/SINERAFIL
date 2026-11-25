from django.db import models


class Customer(models.Model):
    """Tabel CUSTOMER (ERD): id, name, phone."""
    name = models.CharField(max_length=120, verbose_name='Naran Kliente')
    phone = models.CharField(max_length=30, blank=True, verbose_name='Telefone')

    class Meta:
        db_table = 'customer'
        ordering = ['name']
        verbose_name_plural = 'Customer'

    def __str__(self):
        return self.name


class Equipment(models.Model):
    """Tabel EQUIPMENT (ERD): id, customer_id, name, serial_number. Kolun tambahan: plate (plaka)."""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='equipments',
                                 verbose_name='Kliente')
    name = models.CharField(max_length=120, verbose_name='Naran Ekipamentu (Motór)')
    serial_number = models.CharField(max_length=60, blank=True, verbose_name='Nu. Rangka / Mesin')
    plate = models.CharField(max_length=20, blank=True, verbose_name='Plaka')    # tambahan

    class Meta:
        db_table = 'equipment'
        ordering = ['name']
        verbose_name_plural = 'Equipment'

    def __str__(self):
        return '%s%s' % (self.name, ' — %s' % self.plate if self.plate else '')
