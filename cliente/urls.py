from django.urls import path
from . import views

urlpatterns = [
    path('', views.kliente_list, name="kliente-list"),
    path('add/', views.kliente_add, name="kliente-add"),
    path('edit/<int:pk>/', views.kliente_edit, name="kliente-edit"),
    path('delete/<int:pk>/', views.kliente_delete, name="kliente-delete"),

    path('motor/', views.motor_list, name="motor-list"),
    path('motor/add/', views.motor_add, name="motor-add"),
    path('motor/edit/<int:pk>/', views.motor_edit, name="motor-edit"),
    path('motor/delete/<int:pk>/', views.motor_delete, name="motor-delete"),
]
