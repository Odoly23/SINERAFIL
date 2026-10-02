from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_groups(sender, **kwargs):
    """Kria grupu (papél) admin, mekaniku no nain automátiku depois migrate."""
    from django.contrib.auth.models import Group
    for name in ('admin', 'mekaniku', 'nain'):
        Group.objects.get_or_create(name=name)


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        post_migrate.connect(create_groups, sender=self)
