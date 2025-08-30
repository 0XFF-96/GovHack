from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema


@extend_schema(
    summary="计算信任分数",
    description="根据查询和数据源计算信任分数",
    request={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "用户查询"},
            "data_sources": {"type": "array", "items": {"type": "string"}, "description": "数据源列表"},
            "response": {"type": "string", "description": "AI生成的回复"}
        }
    },
    responses={
        200: {
            "type": "object",
            "properties": {
                "trust_score": {"type": "number", "description": "信任分数 (0-1)"},
                "confidence_level": {"type": "string", "description": "置信度等级"},
                "factors": {"type": "object", "description": "影响因子"}
            }
        }
    },
    tags=["信任评分"]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_trust_score(request):
    """计算信任分数"""
    data = request.data
    query = data.get('query', '')
    data_sources = data.get('data_sources', [])
    response = data.get('response', '')
    
    # 模拟信任分数计算
    base_score = 0.7
    
    # 数据源质量评分
    source_score = 0.9 if 'budget_2024_25' in data_sources else 0.6
    
    # 查询复杂度评分
    complexity_score = 0.8 if len(query.split()) > 5 else 0.9
    
    # 最终分数
    trust_score = (base_score + source_score + complexity_score) / 3
    trust_score = min(trust_score, 1.0)
    
    confidence_level = "高" if trust_score >= 0.8 else "中" if trust_score >= 0.6 else "低"
    
    return Response({
        "trust_score": round(trust_score, 3),
        "confidence_level": confidence_level,
        "factors": {
            "data_source_quality": round(source_score, 3),
            "query_complexity": round(complexity_score, 3),
            "response_relevance": round(base_score, 3)
        }
    })


@extend_schema(
    summary="获取信任度指标",
    description="获取系统信任度的各项指标和统计信息",
    responses={
        200: {
            "type": "object",
            "properties": {
                "average_trust_score": {"type": "number"},
                "total_queries": {"type": "integer"},
                "high_confidence_percentage": {"type": "number"},
                "data_source_reliability": {"type": "object"}
            }
        }
    },
    tags=["信任评分"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def trust_metrics(request):
    """获取信任度指标"""
    return Response({
        "average_trust_score": 0.82,
        "total_queries": 1247,
        "high_confidence_percentage": 73.5,
        "data_source_reliability": {
            "budget_2024_25": 0.95,
            "department_expenses": 0.88,
            "policy_impact": 0.79
        }
    })