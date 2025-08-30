"""
Chat API views for handling chat sessions and messages.
"""
import json
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
import uuid
import logging

from .models import ChatSession, ChatMessage, QueryContext
from .serializers import (
    ChatSessionSerializer, ChatMessageSerializer,
    ChatQuerySerializer, ChatResponseSerializer
)
from .services import ai_service

logger = logging.getLogger(__name__)


class ChatSessionListCreateView(generics.ListCreateAPIView):
    """Chat session list and create view"""
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get user's chat sessions"""
        return ChatSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create a new chat session"""
        serializer.save(
            user=self.request.user,
            session_id=str(uuid.uuid4())
        )

    @extend_schema(
        summary="Get chat session list",
        description="Get all chat sessions for the current user",
        responses={200: ChatSessionSerializer(many=True)},
        tags=["Chat"]
    )
    def get(self, request, *args, **kwargs):
        """Get chat session list"""
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Create new chat session",
        description="Create a new chat session",
        responses={201: ChatSessionSerializer},
        tags=["Chat"]
    )
    def post(self, request, *args, **kwargs):
        """Create new chat session"""
        return super().post(request, *args, **kwargs)


class ChatSessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Chat session detail view"""
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'session_id'

    def get_queryset(self):
        """Get user's chat sessions"""
        return ChatSession.objects.filter(user=self.request.user)

    @extend_schema(
        summary="Get chat session details",
        description="Get detailed information for a specific chat session by session_id",
        responses={200: ChatSessionSerializer},
        tags=["Chat"]
    )
    def get(self, request, *args, **kwargs):
        """Get chat session details"""
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update chat session",
        description="Update chat session information (e.g., title)",
        responses={200: ChatSessionSerializer},
        tags=["Chat"]
    )
    def patch(self, request, *args, **kwargs):
        """Update chat session"""
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary="Delete chat session",
        description="Delete the specified chat session and all its messages",
        responses={204: None},
        tags=["Chat"]
    )
    def delete(self, request, *args, **kwargs):
        """Delete chat session"""
        return super().delete(request, *args, **kwargs)


class ChatMessageListView(generics.ListAPIView):
    """Chat message list view"""
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get messages for a chat session"""
        session_id = self.kwargs.get('session_id')
        session = get_object_or_404(ChatSession, session_id=session_id, user=self.request.user)
        return ChatMessage.objects.filter(session=session)

    @extend_schema(
        summary="Get chat message list",
        description="Get all chat messages for the specified session",
        parameters=[
            OpenApiParameter(
                name='session_id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description='Session ID'
            )
        ],
        responses={200: ChatMessageSerializer(many=True)},
        tags=["Chat"]
    )
    def get(self, request, *args, **kwargs):
        """Get chat message list"""
        return super().get(request, *args, **kwargs)


@extend_schema(
    summary="Send chat message",
    description="Send a message to the AI assistant and get a response",
    request=ChatQuerySerializer,
    responses={
        200: ChatResponseSerializer,
        400: {"description": "Bad request parameters"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    },
    examples=[
        OpenApiExample(
            "Basic Query",
            summary="Basic data query example",
            description="Query government department budget information",
            value={
                "query": "What is the education department budget for 2024?",
                "context": {"department": "education"}
            },
            request_only=True,
        ),
        OpenApiExample(
            "Continue Conversation",
            summary="Continue existing conversation",
            description="Continue conversation in existing session",
            value={
                "query": "How does that compare to last year?",
                "session_id": "550e8400-e29b-41d4-a716-446655440000"
            },
            request_only=True,
        )
    ],
    tags=["Chat"]
)
@api_view(['POST'])
@permission_classes([])  # Allow public access for testing
def chat_query(request):
    """
    # AI Chat Query Processing
    
    Send natural language queries to the AI assistant to get intelligent responses
    about Australian government data, budgets, and policies.
    
    ## Request Format
    ```json
    {
        "query": "What is the education department budget for 2024?",
        "context": {"department": "education"},
        "session_id": "optional-session-uuid"
    }
    ```
    
    ## Query Examples
    
    **Budget inquiry:**
    ```json
    {
        "query": "How much does the health department spend on Medicare?",
        "context": {"department": "health", "program": "medicare"}
    }
    ```
    
    **Comparative analysis:**
    ```json
    {
        "query": "Compare education spending between 2023 and 2024",
        "session_id": "existing-session-id"
    }
    ```
    
    **Department overview:**
    ```json
    {
        "query": "Tell me about the Defence department's budget allocation"
    }
    ```
    
    ## Response Format
    ```json
    {
        "session_id": "uuid-string",
        "user_message": {
            "content": "Your question",
            "timestamp": "2024-08-30T10:00:00Z"
        },
        "assistant_message": {
            "content": "AI response with relevant data and insights",
            "trust_score": 0.95,
            "timestamp": "2024-08-30T10:00:01Z"
        },
        "processing_info": {
            "processing_time": 0.15,
            "data_sources_used": ["budget_2024"],
            "intent_detected": "budget_inquiry"
        },
        "trust_score": 0.95
    }
    ```
    
    ## Features
    - 🤖 **Natural Language Processing**: Understands context and intent
    - 📊 **Data Integration**: Accesses real government datasets
    - 🔍 **Trust Scoring**: Provides confidence ratings (0.0-1.0)
    - 💬 **Session Support**: Maintains conversation history
    - ⚡ **Fast Response**: Typical response time < 200ms
    - 🔓 **Public Access**: No authentication required for basic queries
    
    ## Trust Score Interpretation
    - **0.9-1.0**: High confidence - Data directly available
    - **0.7-0.9**: Medium confidence - Calculated or inferred
    - **0.5-0.7**: Lower confidence - Limited data available
    - **0.0-0.5**: Low confidence - Speculative or uncertain
    """
    serializer = ChatQuerySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    query = serializer.validated_data['query']
    session_id = serializer.validated_data.get('session_id')
    context = serializer.validated_data.get('context', {})

    try:
        # Get or create session (support anonymous users)
        user = request.user if request.user.is_authenticated else None

        if session_id:
            if user:
                session = get_object_or_404(ChatSession, session_id=session_id, user=user)
            else:
                # For anonymous users, find session without user filter
                try:
                    session = ChatSession.objects.get(session_id=session_id)
                except ChatSession.DoesNotExist:
                    return Response(
                        {'error': 'Session not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
        else:
            session = ChatSession.objects.create(
                user=user,  # Can be None (anonymous user)
                session_id=str(uuid.uuid4()),
                title=query[:50] + "..." if len(query) > 50 else query
            )

        # Create user message
        user_message = ChatMessage.objects.create(
            session=session,
            message_type='user',
            content=query,
            metadata={'context': context}
        )

        # 调用AI查询服务
        from .ai_service import ai_service
        
        try:
            ai_result = ai_service.process_query(query, context)
            
            if ai_result.get('success'):
                # 构建结构化响应
                response_data = {
                    'answer': ai_result.get('answer', query),
                    'method': ai_result.get('method', 'SQL'),
                    'executed_query': ai_result.get('executed_query'),
                    'data_sources': ai_result.get('data_sources', []),
                    'summary': ai_result.get('summary'),
                    'table_data': ai_result.get('table_data'),
                    'metadata': ai_result.get('metadata', {}),
                    'confidence': ai_result.get('confidence', 0.5)
                }
                
                assistant_response = json.dumps(response_data, ensure_ascii=False, indent=2)
                trust_score = ai_result.get('confidence', 0.5)
                processing_time = 0.0
                data_sources = ai_result.get('data_sources', [])
                intent = 'data_query'
                entities = {}
                model_used = 'ai_service'
            else:
                assistant_response = f"抱歉，处理查询时出现错误: {ai_result.get('error', '未知错误')}"
                trust_score = 0.1
                processing_time = 0.0
                data_sources = []
                intent = 'error'
                entities = {}
                model_used = 'ai_service'
                
        except Exception as e:
            assistant_response = f"AI服务暂时不可用，使用基础响应: {query}\n\n错误: {str(e)}"
            trust_score = 0.3
            processing_time = 0.0
            data_sources = []
            intent = 'error'
            entities = {}
            model_used = 'fallback'

        # Create assistant reply
        assistant_message = ChatMessage.objects.create(
            session=session,
            message_type='assistant',
            content=assistant_response,
            metadata={
                'generated_at': timezone.now().isoformat(),
                'model_used': model_used,
                'processing_time': processing_time,
                'data_sources': data_sources
            },
            trust_score=trust_score
        )

        # Create query context
        QueryContext.objects.create(
            message=user_message,
            extracted_entities=entities,
            intent=intent,
            data_sources=data_sources,
            processing_time=processing_time
        )

        # Update session time
        session.updated_at = timezone.now()
        session.save()

        response_data = {
            'session_id': session.session_id,
            'user_message': ChatMessageSerializer(user_message).data,
            'assistant_message': ChatMessageSerializer(assistant_message).data,
            'processing_info': {
                'processing_time': processing_time,
                'data_sources_used': data_sources,
                'intent_detected': intent,
                'model_used': model_used
            },
            'trust_score': trust_score
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': f'Error processing query: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )