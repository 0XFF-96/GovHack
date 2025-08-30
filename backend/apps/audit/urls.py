from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    path('logs/', views.audit_logs, name='audit-logs'),
    path('user-activity/', views.user_activity, name='user-activity'),
]