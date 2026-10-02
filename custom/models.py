from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

#creates your models here.
class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class BaseModel(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="%(class)s_created")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="%(class)s_updated")
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="%(class)s_deleted")
    deleted_at = models.DateTimeField(null=True, blank=True)
    objects = models.Manager()
    active_objects = ActiveManager()

    def soft_delete(self, user):
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save()

    def restore(self):
        self.deleted_at = None
        self.deleted_by = None
        self.save()

    class Meta:
        abstract = True


class Kategoria(BaseModel):
    name = models.CharField(max_length=80, unique=True, verbose_name="Naran Kategoria")

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Kategoria'

    def __str__(self):
        return self.name
