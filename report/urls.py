from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name="dashboard"),
    path('', views.relatoriu, name="relatoriu"),
    path('nota/<int:pk>/', views.nota_servisu, name="nota-servisu"),
]
