import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.db.models import Q
from accounts.mixins import RiskManagementMixin
from .models import Risk, RiskCategory
from .forms import RiskForm, RiskFilterForm
from audit.models import AuditLog


class RiskListView(LoginRequiredMixin, ListView):
    model = Risk
    template_name = 'risks/risk_list.html'
    context_object_name = 'risks'
    paginate_by = 15

    def get_queryset(self):
        qs = Risk.objects.select_related('category', 'department', 'created_by').prefetch_related('assigned_to')
        f = self.request.GET
        if f.get('search'):
            qs = qs.filter(Q(name__icontains=f['search']) | Q(description__icontains=f['search']))
        if f.get('status'):
            qs = qs.filter(status=f['status'])
        if f.get('category'):
            qs = qs.filter(category_id=f['category'])
        if f.get('severity'):
            qs = qs.filter(severity=f['severity'])
        if f.get('department'):
            qs = qs.filter(department_id=f['department'])

        user = self.request.user
        if user.is_dept_head and user.department:
            qs = qs.filter(department=user.department)

        if user.role == 'risk_officer':
            qs = qs.filter(Q(assigned_to=user) | Q(created_by=user)).distinct()
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['filter_form'] = RiskFilterForm(self.request.GET or None)
        ctx['total_count'] = self.get_queryset().count()
        ctx['open_count'] = self.get_queryset().filter(status='open').count()
        ctx['inprogress_count'] = self.get_queryset().filter(status='in_progress').count()
        ctx['closed_count'] = self.get_queryset().filter(status='closed').count()
        return ctx


class RiskDetailView(LoginRequiredMixin, DetailView):
    model = Risk
    template_name = 'risks/risk_detail.html'
    context_object_name = 'risk'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['history'] = AuditLog.objects.filter(
            target_model='Risk', target_id=str(self.object.pk)
        ).order_by('-timestamp')[:20]
        return ctx


@login_required
def risk_create(request):
    if not request.user.can_manage_risks:
        raise PermissionDenied
    form = RiskForm(request.POST or None, request.FILES or None, user=request.user)
    if request.method == 'POST' and form.is_valid():
        risk = form.save(commit=False)
        risk.created_by = request.user
        risk.save()
        form.save_m2m()

        AuditLog.objects.create(
            user=request.user,
            action=f'Created Risk: {risk.name}',
            target_model='Risk',
            target_id=str(risk.pk),
        )

        _notify_assigned_users(risk, request)
        messages.success(request, f'Risk "{risk.name}" created successfully.')
        return redirect('risks:risk_detail', pk=risk.pk)
    return render(request, 'risks/risk_form.html', {'form': form, 'action': 'Create'})


@login_required
def risk_update(request, pk):
    risk = get_object_or_404(Risk, pk=pk)
    user = request.user

    if not user.can_manage_risks:
        raise PermissionDenied
    if user.is_dept_head and user.department != risk.department:
        raise PermissionDenied
    if user.role == 'risk_officer' and user not in risk.assigned_to.all() and user != risk.created_by:
        raise PermissionDenied

    old_values = {
        'status': risk.status,
        'severity': risk.severity,
        'likelihood': risk.likelihood,
        'due_date': str(risk.due_date) if risk.due_date else None,
        'mitigation_plan': risk.mitigation_plan,
    }
    form = RiskForm(request.POST or None, request.FILES or None, instance=risk, user=user)
    if request.method == 'POST' and form.is_valid():
        risk = form.save()
        new_values = {
            'status': risk.status,
            'severity': risk.severity,
            'likelihood': risk.likelihood,
            'due_date': str(risk.due_date) if risk.due_date else None,
            'mitigation_plan': risk.mitigation_plan,
        }


        changes = []
        for field, old_val in old_values.items():
            new_val = new_values[field]
            if old_val != new_val:
                changes.append(f"{field.replace('_', ' ').title()}: {old_val} → {new_val}")

        action_msg = f'Updated Risk: {risk.name}'
        if changes:
            action_msg += f" ({'; '.join(changes)})"

        AuditLog.objects.create(
            user=request.user,
            action=action_msg,
            target_model='Risk',
            target_id=str(risk.pk),
            old_value=old_values,
            new_value=new_values,
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        new_assigned = set(risk.assigned_to.values_list('pk', flat=True))
        if new_assigned != old_assigned:
            _notify_assigned_users(risk, request)
        messages.success(request, f'Risk "{risk.name}" updated.')
        return redirect('risks:risk_detail', pk=risk.pk)
    return render(request, 'risks/risk_form.html', {'form': form, 'action': 'Edit', 'risk': risk})


@login_required
def risk_delete(request, pk):
    if not request.user.can_manage_org:
        raise PermissionDenied
    risk = get_object_or_404(Risk, pk=pk)
    if request.method == 'POST':
        name = risk.name
        risk.delete()
        AuditLog.objects.create(
            user=request.user,
            action=f'Deleted Risk: {name}',
            target_model='Risk',
            target_id=str(pk),
        )
        messages.success(request, f'Risk "{name}" deleted.')
        return redirect('risks:risk_list')
    return render(request, 'risks/risk_confirm_delete.html', {'risk': risk})


@login_required
def risk_export_csv(request):
    if not request.user.can_manage_risks:
        raise PermissionDenied
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="risks_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Category', 'Severity', 'Likelihood', 'Risk Score',
                     'Status', 'Department', 'Due Date', 'Created By', 'Created At'])
    for r in Risk.objects.select_related('category', 'department', 'created_by').all():
        writer.writerow([
            r.pk, r.name,
            r.category.name if r.category else '',
            r.get_severity_display(), r.get_likelihood_display(), r.risk_score,
            r.get_status_display(),
            r.department.name if r.department else '',
            r.due_date or '',
            r.created_by.username if r.created_by else '',
            r.created_at.strftime('%Y-%m-%d %H:%M'),
        ])
    return response


def _notify_assigned_users(risk, request):
    """Send email notifications to users assigned to the risk."""
    from django.core.mail import send_mail
    from django.conf import settings
    users = risk.assigned_to.filter(email__isnull=False).exclude(email='')
    for user in users:
        try:
            send_mail(
                subject=f'[GMS] Risk Assigned: {risk.name}',
                message=(
                    f'Dear {user.get_full_name() or user.username},\n\n'
                    f'You have been assigned to the following risk:\n'
                    f'  Name: {risk.name}\n'
                    f'  Category: {risk.category}\n'
                    f'  Severity: {risk.get_severity_display()}\n'
                    f'  Status: {risk.get_status_display()}\n'
                    f'  Due Date: {risk.due_date or "Not set"}\n\n'
                    f'Please log in to GMS to review this risk.\n\nGMS Team'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            pass
