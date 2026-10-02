from django.urls import path
from . import views

urlpatterns = [
    path('', views.pesa_list, name="pesa-list"),
    path('add/', views.pesa_add, name="pesa-add"),
    path('detail/<int:pk>/', views.pesa_detail, name="pesa-detail"),
    path('edit/<int:pk>/', views.pesa_edit, name="pesa-edit"),
    path('delete/<int:pk>/', views.pesa_delete, name="pesa-delete"),

    path('movimentu/', views.movimentu_list, name="movimentu-list"),
    path('movimentu/add/', views.movimentu_add, name="movimentu-add"),
]
