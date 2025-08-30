from rest_framework import serializers
from .models import ChatSession, ChatMessage, QueryContext


class ChatSessionSerializer(serializers.ModelSerializer):
    """聊天会话序列化器"""
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = ['id', 'session_id', 'title', 'created_at', 'updated_at', 'is_active', 'message_count']
        read_only_fields = ['id', 'created_at', 'updated_at', 'session_id']
    
    def get_message_count(self, obj):
        return obj.messages.count()


class QueryContextSerializer(serializers.ModelSerializer):
    """查询上下文序列化器"""
    
    class Meta:
        model = QueryContext
        fields = ['extracted_entities', 'intent', 'data_sources', 'processing_time']


class ChatMessageSerializer(serializers.ModelSerializer):
    """聊天消息序列化器"""
    context = QueryContextSerializer(source='querycontext', read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'message_type', 'content', 'metadata', 'trust_score', 'timestamp', 'context']
        read_only_fields = ['id', 'timestamp']


class ChatMessageCreateSerializer(serializers.ModelSerializer):
    """创建聊天消息序列化器"""
    
    class Meta:
        model = ChatMessage
        fields = ['content']
    
    def create(self, validated_data):
        validated_data['message_type'] = 'user'
        return super().create(validated_data)


class ChatQuerySerializer(serializers.Serializer):
    """聊天查询序列化器"""
    query = serializers.CharField(max_length=1000, help_text="用户查询内容")
    session_id = serializers.CharField(max_length=100, required=False, help_text="会话ID，不提供时创建新会话")
    context = serializers.JSONField(required=False, default=dict, help_text="额外上下文信息")
    
    def validate_query(self, value):
        if not value.strip():
            raise serializers.ValidationError("查询内容不能为空")
        return value.strip()


class ChatResponseSerializer(serializers.Serializer):
    """聊天响应序列化器"""
    session_id = serializers.CharField(help_text="会话ID")
    user_message = ChatMessageSerializer(help_text="用户消息")
    assistant_message = ChatMessageSerializer(help_text="助手回复")
    processing_info = serializers.JSONField(help_text="处理信息")
    trust_score = serializers.FloatField(help_text="信任分数")