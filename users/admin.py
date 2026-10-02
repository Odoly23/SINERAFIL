from django.contrib import admin

from .models import AuditLogin, Emp, EmpUser

admin.site.register(Emp)
admin.site.register(EmpUser)
admin.site.register(AuditLogin)
