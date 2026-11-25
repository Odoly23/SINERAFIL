from django.urls import path
from . import views

urlpatterns = [
    path('category/', views.category_list, name="category-list"),
    path('category/add/', views.category_add, name="category-add"),
    path('category/edit/<int:pk>/', views.category_edit, name="category-edit"),
    path('category/delete/<int:pk>/', views.category_delete, name="category-delete"),

    path('supplier/', views.supplier_list, name="supplier-list"),
    path('supplier/add/', views.supplier_add, name="supplier-add"),
    path('supplier/edit/<int:pk>/', views.supplier_edit, name="supplier-edit"),
    path('supplier/delete/<int:pk>/', views.supplier_delete, name="supplier-delete"),
]
