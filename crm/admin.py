from django.contrib import admin
from .models import Client, CallLog


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'phone', 'email']


@admin.register(CallLog)
class CallLogAdmin(admin.ModelAdmin):
    list_display = ['caller_name', 'caller_phone', 'call_type', 'is_new_client', 'created_at']
    list_filter = ['call_type', 'is_new_client', 'created_at']
    search_fields = ['caller_name', 'caller_phone', 'notes']
