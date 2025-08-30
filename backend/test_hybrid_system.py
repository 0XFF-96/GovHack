#!/usr/bin/env python
"""
测试混合路由系统
验证SQL查询、RAG检索和混合查询功能
"""

import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'govhack_backend.settings')
django.setup()

from apps.datasets.models import (
    Portfolio, Department, FinanceRecord, HRRecord, ProcurementRecord
)
from apps.chat.ai_service import AIQueryService
from apps.chat.rag_service import rag_service


def test_hybrid_system():
    """测试混合路由系统"""
    print("🚀 开始测试混合路由系统...")
    print("=" * 60)
    
    # 1. 测试SQL查询
    print("\n📊 测试SQL查询功能:")
    test_sql_queries()
    
    # 2. 测试RAG检索
    print("\n🔍 测试RAG检索功能:")
    test_rag_queries()
    
    # 3. 测试混合查询
    print("\n🔄 测试混合查询功能:")
    test_hybrid_queries()
    
    print("\n✅ 所有测试完成！")


def test_sql_queries():
    """测试SQL查询功能"""
    ai_service = AIQueryService()
    
    sql_test_queries = [
        "What is the total education budget for 2024?",
        "Show me the top 10 highest expenses",
        "Compare department budgets",
        "What is the average budget by portfolio?",
        "How much does the health department spend?"
    ]
    
    for query in sql_test_queries:
        print(f"\n  查询: {query}")
        try:
            result = ai_service.process_query(query)
            if result.get('success'):
                print(f"  ✅ 方法: {result.get('method')}")
                print(f"  📝 回答: {result.get('answer', '')[:100]}...")
                print(f"  🔢 数据源: {', '.join(result.get('data_sources', []))}")
                print(f"  🎯 置信度: {result.get('confidence', 0):.2f}")
            else:
                print(f"  ❌ 失败: {result.get('error', '未知错误')}")
        except Exception as e:
            print(f"  ❌ 异常: {str(e)}")


def test_rag_queries():
    """测试RAG检索功能"""
    ai_service = AIQueryService()
    
    rag_test_queries = [
        "Find details about Supplier Company 1",
        "Tell me about Employee 1's employment record",
        "What contracts does the Health department have?",
        "Find the latest payment records",
        "Show me training records for employees"
    ]
    
    for query in rag_test_queries:
        print(f"\n  查询: {query}")
        try:
            result = ai_service.process_query(query)
            if result.get('success'):
                print(f"  ✅ 方法: {result.get('method')}")
                print(f"  📝 回答: {result.get('answer', '')[:100]}...")
                print(f"  🔢 数据源: {', '.join(result.get('data_sources', []))}")
                print(f"  🎯 置信度: {result.get('confidence', 0):.2f}")
                
                # 显示证据包信息
                evidence = result.get('evidence_package', {})
                if evidence:
                    print(f"  📋 证据包: {len(evidence.get('evidence_items', []))} 项")
            else:
                print(f"  ❌ 失败: {result.get('error', '未知错误')}")
        except Exception as e:
            print(f"  ❌ 异常: {str(e)}")


def test_hybrid_queries():
    """测试混合查询功能"""
    ai_service = AIQueryService()
    
    hybrid_test_queries = [
        "How much does the education department spend and show me the details?",
        "What is the total budget and find related contracts?",
        "Show me budget summary and employee records",
        "Compare department spending and find supplier information"
    ]
    
    for query in hybrid_test_queries:
        print(f"\n  查询: {query}")
        try:
            result = ai_service.process_query(query)
            if result.get('success'):
                print(f"  ✅ 方法: {result.get('method')}")
                print(f"  📝 回答: {result.get('answer', '')[:100]}...")
                print(f"  🔢 数据源: {', '.join(result.get('data_sources', []))}")
                print(f"  🎯 置信度: {result.get('confidence', 0):.2f}")
                
                # 显示混合查询的详细信息
                if result.get('method') == 'HYBRID':
                    sql_result = result.get('sql_result')
                    rag_result = result.get('rag_result')
                    
                    if sql_result:
                        print(f"  📊 SQL结果: {sql_result.get('success', False)}")
                    if rag_result:
                        print(f"  📋 RAG结果: {rag_result.get('success', False)}")
            else:
                print(f"  ❌ 失败: {result.get('error', '未知错误')}")
        except Exception as e:
            print(f"  ❌ 异常: {str(e)}")


def test_rag_service_directly():
    """直接测试RAG服务"""
    print("\n🔧 直接测试RAG服务:")
    
    try:
        # 测试文档搜索
        test_queries = [
            "supplier",
            "employee",
            "contract",
            "payment"
        ]
        
        for query in test_queries:
            print(f"\n  搜索: {query}")
            results = rag_service.search_documents(query)
            print(f"  找到 {len(results)} 条结果")
            
            for i, result in enumerate(results[:2]):  # 只显示前2条
                print(f"    {i+1}. {result.get('source_table')} - {result.get('relevance_score', 0):.2f}")
    
    except Exception as e:
        print(f"  ❌ RAG服务测试失败: {str(e)}")


def check_data_availability():
    """检查数据可用性"""
    print("\n📊 检查数据可用性:")
    
    try:
        portfolios = Portfolio.objects.count()
        departments = Department.objects.count()
        finance_records = FinanceRecord.objects.count()
        hr_records = HRRecord.objects.count()
        procurement_records = ProcurementRecord.objects.count()
        
        print(f"  🏢 部门组合: {portfolios}")
        print(f"  🏛️  部门: {departments}")
        print(f"  💰 财务记录: {finance_records}")
        print(f"  👥 人力资源记录: {hr_records}")
        print(f"  📦 采购记录: {procurement_records}")
        
        if finance_records == 0 or hr_records == 0 or procurement_records == 0:
            print("  ⚠️  建议先运行数据填充命令:")
            print("     python manage.py populate_sample_data --count 20")
            print("     python manage.py vectorize_documents")
        
    except Exception as e:
        print(f"  ❌ 数据检查失败: {str(e)}")


if __name__ == "__main__":
    print("🧪 混合路由系统测试")
    print("=" * 60)
    
    # 检查数据
    check_data_availability()
    
    # 运行测试
    test_hybrid_system()
    
    # 直接测试RAG服务
    test_rag_service_directly()
    
    print("\n🎉 测试完成！")
