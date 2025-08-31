from django.urls import path
from . import views

app_name = 'data_processing'

urlpatterns = [
    path('datasets/', views.dataset_list, name='dataset-list'),
    path('datasets/<str:dataset_id>/', views.dataset_detail, name='dataset-detail'),
    path('search/', views.data_search, name='data-search'),
    path('smart-query/', views.smart_query, name='smart-query'),
]