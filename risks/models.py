from django.db import models
from django.utils.timezone import now
class RiskCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#6c757d')
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Risk Categories'
        ordering = ['name']
class Risk(models.Model):
    class Severity(models.IntegerChoices):
        LOW = 1, 'Low'
        MEDIUM = 2, 'Medium'
        HIGH = 3, 'High'
        CRITICAL = 4, 'Critical'
    class Likelihood(models.IntegerChoices):
        RARE = 1, 'Rare'
        UNLIKELY = 2, 'Unlikely'
        POSSIBLE = 3, 'Possible'
        LIKELY = 4, 'Likely'
        CERTAIN = 5, 'Almost Certain'
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        IN_PROGRESS = 'in_progress', 'In Progress'
        CLOSED = 'closed', 'Closed'
    name = models.CharField(max_length=300)
    description = models.TextField()
    category = models.ForeignKey(
        RiskCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='risks',
    )
    severity = models.IntegerField(choices=Severity.choices, default=Severity.LOW)
    likelihood = models.IntegerField(choices=Likelihood.choices, default=Likelihood.RARE)
    risk_score = models.IntegerField(default=1, editable=False)
    department = models.ForeignKey(
        'organization.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='risks',
    )
    assigned_to = models.ManyToManyField(
        'accounts.User',
        blank=True,
        related_name='assigned_risks',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )
    due_date = models.DateField(null=True, blank=True)
    mitigation_plan = models.TextField(blank=True)
    evidence = models.FileField(upload_to='evidence/', blank=True, null=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_risks',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        self.risk_score = self.severity * self.likelihood
        super().save(*args, **kwargs)
    def __str__(self):
        return f"[{self.get_status_display()}] {self.name}"
    @property
    def severity_label(self):
        if self.risk_score <= 4:
            return 'Low'
        elif self.risk_score <= 8:
            return 'Medium'
        elif self.risk_score <= 12:
            return 'High'
        return 'Critical'
    @property
    def severity_color(self):
        if self.risk_score <= 4:
            return 'success'
        elif self.risk_score <= 8:
            return 'warning'
        elif self.risk_score <= 12:
            return 'danger'
        return 'dark'
    @property
    def is_overdue(self):
        if self.due_date and self.status != self.Status.CLOSED:
            return self.due_date < now().date()
        return False
    class Meta:
        ordering = ['-risk_score', '-created_at']
