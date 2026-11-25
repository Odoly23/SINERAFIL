from django.urls import path
from . import views

urlpatterns = [
	path('Profile/Utilizador/', views.UserProfile, name="UserProfile"),
	path('Profile/Password/', views.change_password, name="change-password"),

    path('list/', views.user_list, name="u-list"),
    path('add/', views.user_add, name="user-add"),
    path('edit/<int:pk>/', views.user_edit, name="user-edit"),
    path('user/reset-password/<int:pk>/', views.reset_password, name='reset-password'),
    path('log/', views.activity_log, name="activity-log"),
]
