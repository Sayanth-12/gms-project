from django import forms
from .models import Organization, Department
from accounts.models import User, Role
class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'description', 'mission', 'vision', 'logo',
                  'address', 'city', 'state', 'country', 'phone', 'email', 'website']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description', 'organization', 'head']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
        self.fields['head'].queryset = User.objects.filter(
            role__in=['dept_head', 'admin', 'super_admin'], is_active=True
        )
        self.fields['head'].required = False
