from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


@extend_schema(
    summary="获取审计日志",
    description="获取系统操作的审计日志记录",
    parameters=[
        OpenApiParameter('start_date', OpenApiTypes.DATE, description='开始日期'),
        OpenApiParameter('end_date', OpenApiTypes.DATE, description='结束日期'),
        OpenApiParameter('action_type', OpenApiTypes.STR, description='操作类型'),
    ],
    responses={
        200: {
            "type": "object",
            "properties": {
                "logs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "timestamp": {"type": "string", "format": "date-time"},
                            "user": {"type": "string"},
                            "action": {"type": "string"},
                            "resource": {"type": "string"},
                            "details": {"type": "object"}
                        }
                    }
                },
                "total": {"type": "integer"}
            }
        }
    },
    tags=["审计追踪"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def audit_logs(request):
    """获取审计日志"""
    # 模拟审计日志数据
    logs = [
        {
            "timestamp": "2024-08-30T13:45:00Z",
            "user": "john.doe",
            "action": "QUERY_EXECUTED",
            "resource": "budget_data",
            "details": {
                "query": "教育部预算查询",
                "trust_score": 0.85,
                "response_time": 0.15
            }
        },
        {
            "timestamp": "2024-08-30T13:42:30Z",
            "user": "jane.smith",
            "action": "SESSION_CREATED",
            "resource": "chat_session",
            "details": {
                "session_id": "550e8400-e29b-41d4-a716-446655440001"
            }
        }
    ]
    
    return Response({
        "logs": logs,
        "total": len(logs)
    })


@extend_schema(
    summary="获取用户活动统计",
    description="获取当前用户的活动统计信息",
    responses={
        200: {
            "type": "object",
            "properties": {
                "total_queries": {"type": "integer"},
                "total_sessions": {"type": "integer"},
                "average_trust_score": {"type": "number"},
                "most_queried_topics": {"type": "array", "items": {"type": "string"}},
                "activity_timeline": {"type": "array", "items": {"type": "object"}}
            }
        }
    },
    tags=["审计追踪"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_activity(request):
    """获取用户活动统计"""
    return Response({
        "total_queries": 25,
        "total_sessions": 8,
        "average_trust_score": 0.82,
        "most_queried_topics": ["教育预算", "健康支出", "基础设施投资"],
        "activity_timeline": [
            {"date": "2024-08-30", "queries": 5, "avg_trust": 0.85},
            {"date": "2024-08-29", "queries": 8, "avg_trust": 0.78},
            {"date": "2024-08-28", "queries": 12, "avg_trust": 0.83}
        ]
    })