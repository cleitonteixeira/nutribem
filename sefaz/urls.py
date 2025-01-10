from django.urls import path
from . import views

app_name = 'sefaz'

urlpatterns = [
    path('nfe/', views.nfe , name="index"),
    path('business/', views.business, name="business"),
] 