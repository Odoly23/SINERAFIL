from django.db import models


class Category(models.Model):
    """Tabel CATEGORY (ERD): id, name."""
    name = models.CharField(max_length=80, unique=True, verbose_name='Naran Kategoria')

    class Meta:
        db_table = 'category'
        ordering = ['name']
        verbose_name_plural = 'Category'

    def __str__(self):
        return self.name


class Supplier(models.Model):
    """Tabel SUPPLIER (ERD): id, name, phone."""
    name = models.CharField(max_length=120, verbose_name='Naran Supplier')
    phone = models.CharField(max_length=30, blank=True, verbose_name='Telefone')

    class Meta:
        db_table = 'supplier'
        ordering = ['name']
        verbose_name_plural = 'Supplier'

    def __str__(self):
        return self.name
