from django.contrib import admin
from .models import Organization, Department
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'city', 'country', 'updated_at']
    search_fields = ['name', 'email']
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'head', 'get_member_count', 'created_at']
    list_filter = ['organization']
    search_fields = ['name']
