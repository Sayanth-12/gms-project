from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User, Role
from .forms import LoginForm, UserRegistrationForm, UserUpdateForm, ProfileUpdateForm
from .mixins import AdminRequiredMixin
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'Welcome back, {user.first_name or user.username}!')
        return redirect(request.GET.get('next', 'dashboard:index'))
    return render(request, 'accounts/login.html', {'form': form})
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')
class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    def get_queryset(self):
        qs = User.objects.select_related('department').order_by('-date_joined')
        role = self.request.GET.get('role', '')
        dept = self.request.GET.get('department', '')
        search = self.request.GET.get('search', '')
        if role:
            qs = qs.filter(role=role)
        if dept:
            qs = qs.filter(department_id=dept)
        if search:
            qs = qs.filter(username__icontains=search) | qs.filter(email__icontains=search)
        return qs
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from organization.models import Department
        ctx['roles'] = Role.choices
        ctx['departments'] = Department.objects.all()
        ctx['role_filter'] = self.request.GET.get('role', '')
        ctx['dept_filter'] = self.request.GET.get('department', '')
        ctx['search'] = self.request.GET.get('search', '')
        return ctx
class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/user_detail.html'
    context_object_name = 'profile_user'
@login_required
def user_create(request):
    if not request.user.can_manage_org:
        raise PermissionDenied
    form = UserRegistrationForm(
        request.POST or None,
        request.FILES or None,
        requesting_user=request.user,
    )
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        messages.success(request, f'User "{user.username}" created successfully.')
        return redirect('accounts:user_list')
    return render(request, 'accounts/user_form.html', {'form': form, 'action': 'Create'})
@login_required
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    if not request.user.can_manage_org and request.user != user:
        raise PermissionDenied
    form = UserUpdateForm(
        request.POST or None,
        request.FILES or None,
        instance=user,
        requesting_user=request.user,
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'User "{user.username}" updated.')
        return redirect('accounts:user_list')
    return render(request, 'accounts/user_form.html', {'form': form, 'action': 'Update', 'target_user': user})
@login_required
def user_delete(request, pk):
    if not request.user.is_super_admin:
        raise PermissionDenied
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.is_active = False
        user.save()
        messages.success(request, f'User "{user.username}" deactivated.')
        return redirect('accounts:user_list')
    return render(request, 'accounts/user_confirm_delete.html', {'target_user': user})
@login_required
def profile_view(request):
    form = ProfileUpdateForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('accounts:profile')
    return render(request, 'accounts/profile.html', {'form': form})
@login_required
def password_change(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Password changed successfully.')
        return redirect('accounts:profile')
    return render(request, 'accounts/password_change.html', {'form': form})
