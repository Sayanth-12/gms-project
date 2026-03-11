from django.urls import path
from . import views
app_name = 'risks'
urlpatterns = [
    path('', views.RiskListView.as_view(), name='risk_list'),
    path('create/', views.risk_create, name='risk_create'),
    path('<int:pk>/', views.RiskDetailView.as_view(), name='risk_detail'),
    path('<int:pk>/edit/', views.risk_update, name='risk_update'),
    path('<int:pk>/delete/', views.risk_delete, name='risk_delete'),
    path('export/csv/', views.risk_export_csv, name='risk_export_csv'),
]
