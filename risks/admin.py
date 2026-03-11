from django.contrib import admin
from .models import Risk, RiskCategory
@admin.register(RiskCategory)
class RiskCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']
    search_fields = ['name']
@admin.register(Risk)
class RiskAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'severity', 'likelihood', 'risk_score', 'status', 'department', 'due_date', 'created_by']
    list_filter = ['status', 'category', 'severity', 'department']
    search_fields = ['name', 'description']
    readonly_fields = ['risk_score', 'created_at', 'updated_at']
    filter_horizontal = ['assigned_to']
