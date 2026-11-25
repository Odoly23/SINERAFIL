from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name="dashboard"),
    path('', views.reports, name="reports"),
    path('invoice/<int:pk>/', views.repair_invoice, name="repair-invoice"),
]
