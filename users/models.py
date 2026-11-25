from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, password=None, role='technician', **extra):
        if not username:
            raise ValueError('Username tenke iha.')
        user = self.model(username=username, role=role, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra):
        extra['role'] = 'admin'
        return self.create_user(username, password, **extra)


class User(AbstractBaseUser):
    """Tabel USER (ERD): id, username, password, role.
    Kolun tambahan: full_name (naran hatudu), is_active (desativa konta)."""
    ADMIN = 'admin'
    TECHNICIAN = 'technician'
    OWNER = 'owner'
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (TECHNICIAN, 'Mekániku (Technician)'),
        (OWNER, "Na'in Ofisina (Owner)"),
    ]

    username = models.CharField(max_length=150, unique=True, verbose_name='Naran utilizadór')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=TECHNICIAN, verbose_name='Papél')
    full_name = models.CharField(max_length=150, blank=True, verbose_name='Naran kompletu')   # tambahan
    is_active = models.BooleanField(default=True, verbose_name='Konta ativu')                  # tambahan
    last_login = None      # ERD la iha last_login

    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'user'
        ordering = ['username']

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        return self.full_name or self.username

    # kompatibilidade ho template/auth Django
    def get_full_name(self):
        return self.display_name


class ActivityLog(models.Model):
    """Tabel ACTIVITY_LOG (ERD): id, user_id, action, created_at."""
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='activity_logs', verbose_name='Utilizadór')
    action = models.CharField(max_length=255, verbose_name='Atividade')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Data/Oras')

    class Meta:
        db_table = 'activity_log'
        ordering = ['-created_at', '-id']

    def __str__(self):
        return '%s: %s' % (self.user, self.action)
