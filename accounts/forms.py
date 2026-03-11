from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import User, Role
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'department',
                  'phone', 'password1', 'password2']
    def __init__(self, *args, **kwargs):
        self.requesting_user = kwargs.pop('requesting_user', None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
        if self.requesting_user and not self.requesting_user.is_super_admin:
            self.fields['role'].choices = [
                c for c in Role.choices if c[0] != Role.SUPER_ADMIN
            ]
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'bio',
                  'profile_image', 'role', 'department', 'is_active']
    def __init__(self, *args, **kwargs):
        self.requesting_user = kwargs.pop('requesting_user', None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
        if self.requesting_user and not self.requesting_user.is_super_admin:
            self.fields['role'].choices = [
                c for c in Role.choices if c[0] != Role.SUPER_ADMIN
            ]
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'bio', 'profile_image']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
