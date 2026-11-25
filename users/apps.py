from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        # Tabel USER (ERD) la iha kolun last_login -> la atualiza last_login bainhira login.
        from django.contrib.auth.models import update_last_login
        from django.contrib.auth.signals import user_logged_in
        user_logged_in.disconnect(update_last_login)
