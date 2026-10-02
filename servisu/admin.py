from django.contrib import admin

from .models import Despeza, Servisu, ServisuPesa

admin.site.register(Servisu)
admin.site.register(ServisuPesa)
admin.site.register(Despeza)
