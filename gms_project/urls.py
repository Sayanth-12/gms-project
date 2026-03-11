from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('organization/', include('organization.urls', namespace='organization')),
    path('risks/', include('risks.urls', namespace='risks')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('audit/', include('audit.urls', namespace='audit')),
    path('', include('dashboard.urls', namespace='home')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
