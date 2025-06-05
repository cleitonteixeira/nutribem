from django.urls import path
from . import views

app_name = 'chatsentinel'

urlpatterns = [
    path('calls/', views.home, name="index"),
]