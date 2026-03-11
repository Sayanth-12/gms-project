from django import forms
from .models import Risk, RiskCategory
from accounts.models import User
class RiskForm(forms.ModelForm):
    class Meta:
        model = Risk
        fields = [
            'name', 'description', 'category', 'severity', 'likelihood',
            'department', 'assigned_to', 'status', 'due_date',
            'mitigation_plan', 'evidence',
        ]
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'assigned_to': forms.SelectMultiple(attrs={'class': 'form-control', 'size': '6'}),
        }
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in ['assigned_to']:
                field.widget.attrs.setdefault('class', 'form-control')
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)
        if self.user and self.user.is_dept_head and self.user.department:
            self.fields['department'].initial = self.user.department
            self.fields['department'].queryset = type(self.fields['department'].queryset.model).objects.filter(
                pk=self.user.department.pk
            )
        if self.user and not self.user.can_manage_org:
            self.fields['status'].choices = [
                c for c in Risk.Status.choices if c[0] != 'closed'
            ]
class RiskFilterForm(forms.Form):
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search risks...'}))
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Statuses')] + Risk.Status.choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    category = forms.ModelChoiceField(
        required=False,
        queryset=RiskCategory.objects.all(),
        empty_label='All Categories',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    severity = forms.ChoiceField(
        required=False,
        choices=[('', 'All Severities')] + Risk.Severity.choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    department = forms.CharField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    def __init__(self, *args, **kwargs):
        from organization.models import Department
        super().__init__(*args, **kwargs)
        dept_choices = [('', 'All Departments')] + [(str(d.pk), d.name) for d in Department.objects.all()]
        self.fields['department'].widget.choices = dept_choices
