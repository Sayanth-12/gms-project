from django.contrib.auth.models import AbstractUser
from django.db import models
class Role(models.TextChoices):
    SUPER_ADMIN = 'super_admin', 'Super Admin'
    ADMIN = 'admin', 'Admin'
    DEPT_HEAD = 'dept_head', 'Department Head'
    RISK_OFFICER = 'risk_officer', 'Risk Officer'
    USER = 'user', 'User'
class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
    )
    department = models.ForeignKey(
        'organization.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
    )
    profile_image = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
    )
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
    @property
    def is_super_admin(self):
        return self.role == Role.SUPER_ADMIN
    @property
    def is_admin(self):
        return self.role in [Role.SUPER_ADMIN, Role.ADMIN]
    @property
    def is_dept_head(self):
        return self.role == Role.DEPT_HEAD
    @property
    def is_risk_officer(self):
        return self.role == Role.RISK_OFFICER
    @property
    def can_manage_risks(self):
        return self.role in [Role.SUPER_ADMIN, Role.ADMIN, Role.DEPT_HEAD, Role.RISK_OFFICER]
    @property
    def can_manage_org(self):
        return self.role in [Role.SUPER_ADMIN, Role.ADMIN]
