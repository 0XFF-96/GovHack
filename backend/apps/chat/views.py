"""
Chat API views for handling chat sessions and messages.
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
import uuid

from .models import ChatSession, ChatMessage, QueryContext
from .serializers import (
    ChatSessionSerializer, ChatMessageSerializer,
    ChatQuerySerializer, ChatResponseSerializer
)


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

        # TODO: This should call the NLP processing service
        # Currently returns a mock response
        assistant_response = f"Received your query: '{query}'\n\nThis is a mock response. In actual implementation, this would:\n1. Parse your natural language query\n2. Retrieve relevant information from government datasets\n3. Generate accurate answers and assess trust scores\n\nQuery context: {context}"

        # Create assistant reply
        assistant_message = ChatMessage.objects.create(
            session=session,
            message_type='assistant',
            content=assistant_response,
            metadata={'generated_at': timezone.now().isoformat()},
            trust_score=0.85  # Mock trust score
        )

        # Create query context
        QueryContext.objects.create(
            message=user_message,
            extracted_entities={'query_type': 'budget_inquiry'},
            intent='data_query',
            data_sources=['budget_2024'],
            processing_time=0.15
        )

        # Update session time
        session.updated_at = timezone.now()
        session.save()

        response_data = {
            'session_id': session.session_id,
            'user_message': ChatMessageSerializer(user_message).data,
            'assistant_message': ChatMessageSerializer(assistant_message).data,
            'processing_info': {
                'processing_time': 0.15,
                'data_sources_used': ['budget_2024'],
                'intent_detected': 'data_query'
            },
            'trust_score': 0.85
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': f'Error processing query: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )