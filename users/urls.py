from django.urls import path
from . import views

urlpatterns = [
	path('Profile/Utilizador/', views.UserProfile, name="UserProfile"),
	path('Profile/Password/', views.change_password, name="change-password"),

    path('list/', views.PList, name="u-list"),
    path('add/', views.EmpAdd, name="user-add"),
    path('emp/<int:pk>/', views.emp_detail, name='emp-detail'),
    path('emp/<int:pk>/update/', views.emp_update, name='emp-update'),
    path('emp/<int:pk>/delete/', views.emp_delete, name='emp-delete'),
    path('user/reset-password/<int:pk>/', views.reset_password, name='reset-password'),
]
