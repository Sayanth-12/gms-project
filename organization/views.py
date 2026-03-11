from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.mixins import AdminRequiredMixin
from .models import Organization, Department
from .forms import OrganizationForm, DepartmentForm
from accounts.models import User
@login_required
def org_detail(request):
    org = Organization.objects.first()
    return render(request, 'organization/org_detail.html', {'org': org})
@login_required
def org_update(request):
    if not request.user.can_manage_org:
        raise PermissionDenied
    org = Organization.objects.first()
    form = OrganizationForm(request.POST or None, request.FILES or None, instance=org)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Organization updated successfully.')
        return redirect('organization:org_detail')
    return render(request, 'organization/org_form.html', {'form': form, 'org': org})
@login_required
def org_create(request):
    if not request.user.can_manage_org:
        raise PermissionDenied
    if Organization.objects.exists():
        return redirect('organization:org_update')
    form = OrganizationForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Organization created.')
        return redirect('organization:org_detail')
    return render(request, 'organization/org_form.html', {'form': form})
class DepartmentListView(LoginRequiredMixin, ListView):
    model = Department
    template_name = 'organization/dept_list.html'
    context_object_name = 'departments'
    def get_queryset(self):
        return Department.objects.select_related('organization', 'head').prefetch_related('members')
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_departments'] = Department.objects.count()
        return ctx
class DepartmentDetailView(LoginRequiredMixin, DetailView):
    model = Department
    template_name = 'organization/dept_detail.html'
    context_object_name = 'dept'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['members'] = self.object.members.filter(is_active=True)
        ctx['risks'] = self.object.risks.order_by('-risk_score')[:5]
        return ctx
@login_required
def dept_create(request):
    if not request.user.can_manage_org:
        raise PermissionDenied
    org = Organization.objects.first()
    if not org:
        messages.warning(request, 'Create an Organization first.')
        return redirect('organization:org_create')
    form = DepartmentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        dept = form.save()
        messages.success(request, f'Department "{dept.name}" created.')
        return redirect('organization:dept_list')
    return render(request, 'organization/dept_form.html', {'form': form, 'action': 'Create'})
@login_required
def dept_update(request, pk):
    if not request.user.can_manage_org:
        raise PermissionDenied
    dept = get_object_or_404(Department, pk=pk)
    form = DepartmentForm(request.POST or None, instance=dept)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Department "{dept.name}" updated.')
        return redirect('organization:dept_list')
    return render(request, 'organization/dept_form.html', {'form': form, 'action': 'Edit', 'dept': dept})
@login_required
def dept_delete(request, pk):
    if not request.user.can_manage_org:
        raise PermissionDenied
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        dept.delete()
        messages.success(request, f'Department "{dept.name}" deleted.')
        return redirect('organization:dept_list')
    return render(request, 'organization/dept_confirm_delete.html', {'dept': dept})
