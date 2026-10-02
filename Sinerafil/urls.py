"""URL configuration ba projetu Sinerafil."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from main.views import loginPage, logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', loginPage, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', include('main.urls')),
    path('custom/', include('custom.urls')),
    path('Utilizadores/', include('users.urls')),
    path('Pesa/', include('pesa.urls')),
    path('Kliente/', include('cliente.urls')),
    path('Servisu/', include('servisu.urls')),
    path('Relatoriu/', include('report.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'main.views.error_404'
handler500 = 'main.views.error_500'
