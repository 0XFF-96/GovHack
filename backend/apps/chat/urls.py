from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # 聊天会话管理
    path('sessions/', views.ChatSessionListCreateView.as_view(), name='session-list-create'),
    path('sessions/<str:session_id>/', views.ChatSessionDetailView.as_view(), name='session-detail'),
    path('sessions/<str:session_id>/messages/', views.ChatMessageListView.as_view(), name='message-list'),
    
    # 聊天查询
    path('query/', views.chat_query, name='chat-query'),
]