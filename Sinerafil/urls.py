"""URL configuration ba projetu Sinerafil."""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from main.views import loginPage, logout_view

urlpatterns = [
    path('', loginPage, name='index'),                    # Start -> System Login
    path('login/', loginPage, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', include('main.urls')),
    path('custom/', include('custom.urls')),
    path('Utilizadores/', include('users.urls')),
    path('Inventory/', include('inventory.urls')),
    path('Customers/', include('customers.urls')),
    path('Repairs/', include('repairs.urls')),
    path('Reports/', include('report.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'main.views.error_404'
handler500 = 'main.views.error_500'
