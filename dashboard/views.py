from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Count, Q
from django.http import JsonResponse
from django.utils.timezone import now
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'
    def get_context_data(self, **kwargs):
        from risks.models import Risk
        from organization.models import Department
        from accounts.models import User
        from audit.models import AuditLog
        ctx = super().get_context_data(**kwargs)
        risks = Risk.objects.all()
        user = self.request.user
        if user.is_dept_head and user.department:
            risks = risks.filter(department=user.department)
        elif user.role == 'risk_officer':
            risks = risks.filter(Q(assigned_to=user) | Q(created_by=user)).distinct()
        today = now().date()
        ctx.update({
            'total_risks': risks.count(),
            'open_risks': risks.filter(status='open').count(),
            'inprogress_risks': risks.filter(status='in_progress').count(),
            'closed_risks': risks.filter(status='closed').count(),
            'overdue_risks': risks.filter(due_date__lt=today).exclude(status='closed').count(),
            'critical_risks': risks.filter(risk_score__gte=12).count(),
            'recent_risks': risks.order_by('-created_at')[:5],
            'overdue_list': risks.filter(due_date__lt=today).exclude(status='closed').order_by('due_date')[:5],
            'recent_logs': AuditLog.objects.select_related('user').order_by('-timestamp')[:8],
            'total_users': User.objects.filter(is_active=True).count(),
            'total_depts': Department.objects.count(),
        })
        return ctx
def chart_risk_by_status(request):
    from risks.models import Risk
    data = Risk.objects.values('status').annotate(count=Count('id'))
    labels = [d['status'].replace('_', ' ').title() for d in data]
    counts = [d['count'] for d in data]
    colors = []
    color_map = {'open': '#dc3545', 'in_progress': '#ffc107', 'closed': '#198754'}
    for d in data:
        colors.append(color_map.get(d['status'], '#6c757d'))
    return JsonResponse({'labels': labels, 'counts': counts, 'colors': colors})
def chart_risk_by_department(request):
    from risks.models import Risk
    data = (Risk.objects
            .values('department__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:10])
    labels = [d['department__name'] or 'Unassigned' for d in data]
    counts = [d['count'] for d in data]
    return JsonResponse({'labels': labels, 'counts': counts})
def chart_risk_by_severity(request):
    from risks.models import Risk
    ranges = [
        ('Low (1-4)', Q(risk_score__lte=4)),
        ('Medium (5-8)', Q(risk_score__gte=5, risk_score__lte=8)),
        ('High (9-12)', Q(risk_score__gte=9, risk_score__lte=12)),
        ('Critical (13+)', Q(risk_score__gte=13)),
    ]
    labels = [r[0] for r in ranges]
    counts = [Risk.objects.filter(r[1]).count() for r in ranges]
    colors = ['#0dcaf0', '#ffc107', '#fd7e14', '#dc3545']
    return JsonResponse({'labels': labels, 'counts': counts, 'colors': colors})
