from django.urls import path
from . import views
app_name = 'organization'
urlpatterns = [
    path('', views.org_detail, name='org_detail'),
    path('create/', views.org_create, name='org_create'),
    path('edit/', views.org_update, name='org_update'),
    path('departments/', views.DepartmentListView.as_view(), name='dept_list'),
    path('departments/create/', views.dept_create, name='dept_create'),
    path('departments/<int:pk>/', views.DepartmentDetailView.as_view(), name='dept_detail'),
    path('departments/<int:pk>/edit/', views.dept_update, name='dept_update'),
    path('departments/<int:pk>/delete/', views.dept_delete, name='dept_delete'),
]
