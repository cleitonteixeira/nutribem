from django.urls import path
from . import views

app_name = 'validation'

urlpatterns = [
    path('login/', views.LoginView, name='login'),
    path('logout/', views.logoutView, name='logout'),
    path('change_password/', views.ChangePassWordView, name='change_password'),
    path('profile/', views.ProfileView, name='profile'),
]