from django.urls import path
from . import views

urlpatterns = [
    path('', views.customer_list, name="customer-list"),
    path('add/', views.customer_add, name="customer-add"),
    path('edit/<int:pk>/', views.customer_edit, name="customer-edit"),
    path('delete/<int:pk>/', views.customer_delete, name="customer-delete"),

    path('equipment/', views.equipment_list, name="equipment-list"),
    path('equipment/add/', views.equipment_add, name="equipment-add"),
    path('equipment/edit/<int:pk>/', views.equipment_edit, name="equipment-edit"),
    path('equipment/delete/<int:pk>/', views.equipment_delete, name="equipment-delete"),
]
