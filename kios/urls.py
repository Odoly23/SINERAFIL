from django.urls import path
from . import views

urlpatterns = [
    path('', views.kios, name="kios"),
    path('scan/', views.kios_scan, name="kios-scan"),
    path('cari/', views.kios_cari, name="kios-cari"),
    path('checkout/', views.kios_checkout, name="kios-checkout"),
    path('istoria/', views.faan_list, name="faan-list"),
    path('detail/<int:pk>/', views.faan_detail, name="faan-detail"),
    path('struk/<int:pk>/', views.faan_struk, name="faan-struk"),
    path('pdf/<int:pk>/', views.faan_pdf, name="faan-pdf"),
    path('void/<int:pk>/', views.faan_void, name="faan-void"),
]
