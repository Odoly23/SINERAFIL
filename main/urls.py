from django.urls import path
from . import views

urlpatterns = [
    path('tentang/', views.about, name="about"),
]
