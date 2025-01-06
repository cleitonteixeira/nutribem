from django.urls import path
from . import views

app_name = 'billings'

urlpatterns = [
    path("/", views.home, name="index"),
    path('invoices/',views.invoices, name="invoices"),
    path('invoice/<int:id>', views.invoice, name="invoice"),
    path('costs/', views.costs, name="costs"),
    path('dashboard_faturamento/', views.dashboard_faturamento, name="dashboard_faturamento"),
    path('requests/', views.requests, name="requests"),
    path('dre/', views.dre, name="dre"),
    path('expenses_cr/', views.expenses_cr, name="expenses_cr"),
    path('expenses_type/', views.expenses_type, name="expenses_type"),
    path('synchronization/', views.synchronization, name="synchronization"),
    path('history/', views.history, name="history"),
    path('hora_extra/', views.HoraExtras, name="hora_extra"),
    path('requisition/<int:id>', views.requisition, name="requisition"),
    path('group_events/', views.groupEvents, name="group_events"),
] 