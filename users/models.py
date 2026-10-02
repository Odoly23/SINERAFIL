import uuid
from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

from custom.models import BaseModel


class Emp(BaseModel):
    name = models.CharField(max_length=100, verbose_name='Naran', null=True)
    sexo = models.CharField(max_length=4, null=True, choices=[('Mane','Mane'),('Feto','Feto')])
    phone = models.CharField(max_length=15, verbose_name="Nu. Telf.", validators=[RegexValidator(r'^\+?670\d{7,8}$', 'Format: +6707xxxxxxx')], null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    persen_ongkos = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('10.00'),
        verbose_name='Persentajen ongkos mekániku (%)',
        help_text="Parte husi ongkos servisu ne'ebé mekániku simu.")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class EmpUser(BaseModel):
    emp = models.OneToOneField(Emp, on_delete=models.CASCADE, related_name="account", null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.emp.name} - {self.user.username}'


class AuditLogin(models.Model):
    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('mekaniku', 'Mekaniku'),
        ('nain', "Na'in Ofisina"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="audit_logins")
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, null=True, blank=True)
    login_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.logout_time and self.login_time:
            self.duration = self.logout_time - self.login_time
            self.is_active = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.username} - {self.login_time.strftime("%d/%m/%Y %H:%M")}'
