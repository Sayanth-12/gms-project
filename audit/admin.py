from django.contrib import admin
from .models import AuditLog
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'user', 'action', 'target_model', 'target_id', 'ip_address']
    list_filter = ['target_model', 'user']
    search_fields = ['action', 'user__username']
    readonly_fields = ['timestamp', 'user', 'action', 'target_model', 'target_id', 'old_value', 'new_value', 'ip_address']
