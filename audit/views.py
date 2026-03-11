from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from accounts.mixins import AdminRequiredMixin
from .models import AuditLog
class AuditLogListView(AdminRequiredMixin, ListView):
    model = AuditLog
    template_name = 'audit/audit_log_list.html'
    context_object_name = 'logs'
    paginate_by = 30
    def get_queryset(self):
        qs = AuditLog.objects.select_related('user').order_by('-timestamp')
        model = self.request.GET.get('model', '')
        user = self.request.GET.get('user', '')
        if model:
            qs = qs.filter(target_model__icontains=model)
        if user:
            qs = qs.filter(user__username__icontains=user)
        return qs
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['model_filter'] = self.request.GET.get('model', '')
        ctx['user_filter'] = self.request.GET.get('user', '')
        return ctx
