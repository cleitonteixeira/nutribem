from django.urls import path
from . import views

app_name = 'synchronize'

urlpatterns = [
   path('', views.synchronize, name='synchronize'),
] 