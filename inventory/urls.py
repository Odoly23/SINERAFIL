from django.urls import path
from . import views

urlpatterns = [
    path('', views.part_list, name="part-list"),
    path('add/', views.part_add, name="part-add"),
    path('detail/<int:pk>/', views.part_detail, name="part-detail"),
    path('edit/<int:pk>/', views.part_edit, name="part-edit"),
    path('delete/<int:pk>/', views.part_delete, name="part-delete"),

    path('movement/', views.movement_list, name="movement-list"),
    path('movement/add/', views.movement_add, name="movement-add"),
]
