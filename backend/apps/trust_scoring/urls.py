from django.urls import path
from . import views

app_name = 'trust_scoring'

urlpatterns = [
    path('score/', views.calculate_trust_score, name='calculate-score'),
    path('metrics/', views.trust_metrics, name='trust-metrics'),
]