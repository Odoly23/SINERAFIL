from django.urls import path
from . import views

urlpatterns = [
    path('', views.repair_list, name="repair-list"),
    path('add/', views.repair_add, name="repair-add"),
    path('detail/<int:pk>/', views.repair_detail, name="repair-detail"),
    path('edit/<int:pk>/', views.repair_edit, name="repair-edit"),
    path('delete/<int:pk>/', views.repair_delete, name="repair-delete"),

    path('<int:pk>/diagnose/', views.repair_diagnose, name="repair-diagnose"),
    path('<int:pk>/assign/', views.repair_assign, name="repair-assign"),
    path('<int:pk>/part/add/', views.repair_part_add, name="repair-part-add"),
    path('<int:pk>/part/<int:item_pk>/remove/', views.repair_part_remove, name="repair-part-remove"),
    path('<int:pk>/start/', views.repair_start, name="repair-start"),
    path('<int:pk>/complete/', views.repair_complete, name="repair-complete"),
]
