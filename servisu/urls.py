from django.urls import path
from . import views

urlpatterns = [
    path('', views.servisu_list, name="servisu-list"),
    path('add/', views.servisu_add, name="servisu-add"),
    path('detail/<int:pk>/', views.servisu_detail, name="servisu-detail"),
    path('edit/<int:pk>/', views.servisu_edit, name="servisu-edit"),
    path('delete/<int:pk>/', views.servisu_delete, name="servisu-delete"),
    path('<int:pk>/pesa/add/', views.servisu_pesa_add, name="servisu-pesa-add"),
    path('<int:pk>/pesa/<int:item_pk>/remove/', views.servisu_pesa_remove, name="servisu-pesa-remove"),

    path('despeza/', views.despeza_list, name="despeza-list"),
    path('despeza/add/', views.despeza_add, name="despeza-add"),
    path('despeza/edit/<int:pk>/', views.despeza_edit, name="despeza-edit"),
    path('despeza/delete/<int:pk>/', views.despeza_delete, name="despeza-delete"),
]
