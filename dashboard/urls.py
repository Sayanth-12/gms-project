from django.urls import path
from . import views
app_name = 'dashboard'
urlpatterns = [
    path('', views.DashboardView.as_view(), name='index'),
    path('charts/status/', views.chart_risk_by_status, name='chart_status'),
    path('charts/department/', views.chart_risk_by_department, name='chart_dept'),
    path('charts/severity/', views.chart_risk_by_severity, name='chart_severity'),
]
