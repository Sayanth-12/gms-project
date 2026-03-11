import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('organization', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='RiskCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('color', models.CharField(default='#6c757d', max_length=7)),
            ],
            options={
                'verbose_name_plural': 'Risk Categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Risk',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('description', models.TextField()),
                ('severity', models.IntegerField(choices=[(1, 'Low'), (2, 'Medium'), (3, 'High'), (4, 'Critical')], default=1)),
                ('likelihood', models.IntegerField(choices=[(1, 'Rare'), (2, 'Unlikely'), (3, 'Possible'), (4, 'Likely'), (5, 'Almost Certain')], default=1)),
                ('risk_score', models.IntegerField(default=1, editable=False)),
                ('status', models.CharField(choices=[('open', 'Open'), ('in_progress', 'In Progress'), ('closed', 'Closed')], default='open', max_length=20)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('mitigation_plan', models.TextField(blank=True)),
                ('evidence', models.FileField(blank=True, null=True, upload_to='evidence/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_to', models.ManyToManyField(blank=True, related_name='assigned_risks', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_risks', to=settings.AUTH_USER_MODEL)),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='risks', to='organization.department')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='risks', to='risks.riskcategory')),
            ],
            options={
                'ordering': ['-risk_score', '-created_at'],
            },
        ),
    ]
