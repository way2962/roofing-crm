from django.contrib import admin
from .models import Client, CallLog, Appointment


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'phone', 'email']


@admin.register(CallLog)
class CallLogAdmin(admin.ModelAdmin):
    list_display = ['caller_name', 'caller_phone', 'call_type', 'inquiry_type', 'is_new_client', 'from_ivr', 'created_at']
    list_filter = ['call_type', 'inquiry_type', 'is_new_client', 'from_ivr', 'created_at']
    search_fields = ['caller_name', 'caller_phone', 'notes']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['caller_name', 'caller_phone', 'is_emergency', 'status', 'scheduled_date', 'from_ivr', 'created_at']
    list_filter = ['is_emergency', 'status', 'from_ivr']
    search_fields = ['caller_name', 'caller_phone', 'reason']
