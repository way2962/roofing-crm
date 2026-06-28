from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('clients/', views.client_list, name='client_list'),
    path('clients/<int:client_id>/', views.client_detail, name='client_detail'),
    path('log-call/', views.call_log_create, name='call_log_create'),
    path('lookup-phone/', views.lookup_phone, name='lookup_phone'),
]
