from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name="dashboard"),
    path('', views.relatoriu, name="relatoriu"),
    path('label-barcode/', views.pesa_label, name="pesa-label"),
    path('nota/<int:pk>/', views.nota_servisu, name="nota-servisu"),
]
