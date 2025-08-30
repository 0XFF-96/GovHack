#!/bin/bash

# API测试脚本

BASE_URL="http://localhost:8000"
echo "🧪 测试GovHack API端点..."
echo "基础URL: $BASE_URL"
echo "================================"

# 测试根路径重定向
echo "📋 测试根路径 (/) - 应该重定向到API文档"
curl -s -o /dev/null -w "状态码: %{http_code}, 重定向到: %{redirect_url}\n" "$BASE_URL/"

# 测试API根路径
echo ""
echo "📋 测试API根路径 (/api/)"
curl -s "$BASE_URL/api/" | python3 -m json.tool 2>/dev/null || echo "❌ JSON响应格式错误"

# 测试健康检查
echo ""
echo "🏥 测试健康检查 (/api/health/)"
curl -s "$BASE_URL/api/health/" | python3 -m json.tool 2>/dev/null || echo "❌ 健康检查失败"

# 测试API文档
echo ""
echo "📚 测试API文档访问 (/api/docs/)"
DOC_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/docs/")
if [ "$DOC_STATUS" = "200" ]; then
    echo "✅ API文档可正常访问"
else
    echo "❌ API文档访问失败，状态码: $DOC_STATUS"
fi

# 测试数据集API
echo ""
echo "📊 测试部门组合列表 (/api/v1/datasets/portfolios/)"
PORTFOLIO_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/v1/datasets/portfolios/")
if [ "$PORTFOLIO_STATUS" = "200" ]; then
    echo "✅ 部门组合API可正常访问"
    PORTFOLIO_COUNT=$(curl -s "$BASE_URL/api/v1/datasets/portfolios/" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
    echo "   部门组合数量: $PORTFOLIO_COUNT"
else
    echo "❌ 部门组合API访问失败，状态码: $PORTFOLIO_STATUS"
fi

# 测试数据统计
echo ""
echo "📈 测试数据统计 (/api/v1/datasets/stats/overview/)"
STATS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/v1/datasets/stats/overview/")
if [ "$STATS_STATUS" = "200" ]; then
    echo "✅ 数据统计API可正常访问"
else
    echo "❌ 数据统计API访问失败，状态码: $STATS_STATUS"
fi

echo ""
echo "================================"
echo "🎯 可用链接:"
echo "   🌐 Swagger文档: $BASE_URL/api/docs/"
echo "   📖 ReDoc文档:   $BASE_URL/api/redoc/"
echo "   🔍 健康检查:     $BASE_URL/api/health/"
echo "   📊 API根路径:    $BASE_URL/api/"