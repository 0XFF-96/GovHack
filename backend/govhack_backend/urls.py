"""
GovHack Backend URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.shortcuts import redirect
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)
from apps.health.views import health_check


def api_root(request):
    """API根目录视图"""
    return JsonResponse({
        'message': '欢迎使用GovHack API',
        'version': '1.0.0',
        'description': '澳大利亚政府数据交互对话系统API',
        'endpoints': {
            'api_docs': request.build_absolute_uri('/api/docs/'),
            'redoc': request.build_absolute_uri('/api/redoc/'),
            'health': request.build_absolute_uri('/api/health/'),
            'admin': request.build_absolute_uri('/admin/'),
        },
        'api_modules': {
            'chat': request.build_absolute_uri('/api/v1/chat/'),
            'datasets': request.build_absolute_uri('/api/v1/datasets/'),
            'data_processing': request.build_absolute_uri('/api/v1/data/'),
            'trust_scoring': request.build_absolute_uri('/api/v1/trust/'),
            'audit': request.build_absolute_uri('/api/v1/audit/'),
        }
    })


def root_redirect(request):
    """根路径重定向到API文档"""
    return redirect('/api/docs/')

urlpatterns = [
    # Root paths
    path('', root_redirect, name='root'),
    path('api/', api_root, name='api-root'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # Health Check
    path('api/health/', health_check, name='health-check'),
    
    # API Schema (OpenAPI/Swagger)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API v1
    path('api/v1/chat/', include('apps.chat.urls')),
    path('api/v1/data/', include('apps.data_processing.urls')),
    path('api/v1/trust/', include('apps.trust_scoring.urls')),
    path('api/v1/audit/', include('apps.audit.urls')),
    path('api/v1/datasets/', include('apps.datasets.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)