from django.urls import path
from . import views

urlpatterns = [
    path('kategoria/', views.kategoria_list, name="kategoria-list"),
    path('kategoria/add/', views.kategoria_add, name="kategoria-add"),
    path('kategoria/edit/<int:pk>/', views.kategoria_edit, name="kategoria-edit"),
    path('kategoria/delete/<int:pk>/', views.kategoria_delete, name="kategoria-delete"),
]
