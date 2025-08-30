from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ChatSession(models.Model):
    """聊天会话模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='用户')
    session_id = models.CharField(max_length=100, unique=True, verbose_name='会话ID')
    title = models.CharField(max_length=200, blank=True, verbose_name='会话标题')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_active = models.BooleanField(default=True, verbose_name='是否活跃')
    
    class Meta:
        db_table = 'chat_session'
        verbose_name = '聊天会话'
        verbose_name_plural = '聊天会话'
        ordering = ['-updated_at']
    
    def __str__(self):
        username = self.user.username if self.user else "匿名用户"
        return f"{username} - {self.title or self.session_id}"


class ChatMessage(models.Model):
    """聊天消息模型"""
    MESSAGE_TYPES = [
        ('user', '用户消息'),
        ('assistant', '助手回复'),
        ('system', '系统消息'),
    ]
    
    session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE, verbose_name='会话')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, verbose_name='消息类型')
    content = models.TextField(verbose_name='消息内容')
    metadata = models.JSONField(default=dict, blank=True, verbose_name='元数据')
    trust_score = models.FloatField(null=True, blank=True, verbose_name='信任分数')
    timestamp = models.DateTimeField(default=timezone.now, verbose_name='时间戳')
    
    class Meta:
        db_table = 'chat_message'
        verbose_name = '聊天消息'
        verbose_name_plural = '聊天消息'
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.session.session_id} - {self.message_type} - {self.content[:50]}"


class QueryContext(models.Model):
    """查询上下文模型"""
    message = models.OneToOneField(ChatMessage, on_delete=models.CASCADE, verbose_name='消息')
    extracted_entities = models.JSONField(default=dict, verbose_name='提取的实体')
    intent = models.CharField(max_length=100, blank=True, verbose_name='意图')
    data_sources = models.JSONField(default=list, verbose_name='数据源')
    processing_time = models.FloatField(null=True, blank=True, verbose_name='处理时间(秒)')
    
    class Meta:
        db_table = 'query_context'
        verbose_name = '查询上下文'
        verbose_name_plural = '查询上下文'