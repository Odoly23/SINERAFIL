from django.db import models

from custom.models import BaseModel


class Kliente(BaseModel):
    name = models.CharField(max_length=120, verbose_name='Naran Kliente')
    phone = models.CharField(max_length=30, blank=True, verbose_name='Telefone')
    address = models.CharField(max_length=200, blank=True, verbose_name='Enderesu')

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Kliente'

    def __str__(self):
        return self.name


class Motor(BaseModel):
    kliente = models.ForeignKey(Kliente, on_delete=models.CASCADE, related_name='motors', verbose_name='Kliente')
    plate = models.CharField(max_length=20, unique=True, verbose_name='Plaka')
    brand = models.CharField(max_length=60, verbose_name='Marka')
    model_name = models.CharField(max_length=60, blank=True, verbose_name='Tipu / Modelu')
    year = models.PositiveIntegerField(null=True, blank=True, verbose_name='Tinan')
    color = models.CharField(max_length=30, blank=True, verbose_name='Kór')

    class Meta:
        ordering = ['plate']
        verbose_name_plural = 'Motór'

    def __str__(self):
        return '%s — %s %s' % (self.plate, self.brand, self.model_name)
