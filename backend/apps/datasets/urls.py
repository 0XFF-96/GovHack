from django.urls import path
from . import views

app_name = 'datasets'

urlpatterns = [
    # 数据集管理
    path('portfolios/', views.portfolio_list, name='portfolio-list'),
    path('portfolios/<uuid:portfolio_id>/', views.portfolio_detail, name='portfolio-detail'),
    path('departments/', views.department_list, name='department-list'),
    path('departments/<uuid:department_id>/', views.department_detail, name='department-detail'),
    
    # 预算查询
    path('budget/search/', views.budget_search, name='budget-search'),
    path('budget/summary/', views.budget_summary, name='budget-summary'),
    path('budget/trends/', views.budget_trends, name='budget-trends'),
    
    # 数据导入
    path('import/status/', views.import_status, name='import-status'),
    path('import/logs/', views.import_logs, name='import-logs'),
    
    # 数据统计
    path('stats/overview/', views.stats_overview, name='stats-overview'),
]