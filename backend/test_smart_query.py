#!/usr/bin/env python3
"""
测试智能查询系统
"""

import requests
import json
import time

def test_smart_query_system():
    """测试智能查询系统"""
    base_url = "http://localhost:8000/api/v1/data-processing/smart-query/"
    
    # 测试查询列表
    test_queries = [
        {
            "name": "Education Budget Query",
            "query": "What is the total education budget for 2024?",
            "expected_method": "SQL"
        },
        {
            "name": "Top Expenses Query", 
            "query": "Show me the top 10 highest expenses",
            "expected_method": "SQL"
        },
        {
            "name": "Portfolio Comparison Query",
            "query": "Compare department budgets by portfolio",
            "expected_method": "SQL"
        },
        {
            "name": "Average Budget Query",
            "query": "What is the average budget by department?",
            "expected_method": "SQL"
        },
        {
            "name": "General Budget Query",
            "query": "Show me the general budget overview",
            "expected_method": "SQL"
        }
    ]
    
    print("🧪 测试智能查询系统")
    print("=" * 50)
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n📝 测试 {i}: {test_case['name']}")
        print(f"查询: {test_case['query']}")
        print(f"预期方法: {test_case['expected_method']}")
        
        try:
            # 发送查询请求
            response = requests.post(
                base_url,
                json={
                    "query": test_case['query'],
                    "context": {},
                    "method_preference": "auto"
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ 查询成功")
                print(f"实际方法: {data.get('method', 'UNKNOWN')}")
                print(f"置信度: {data.get('confidence_score', 0):.2f}")
                print(f"处理时间: {data.get('processing_time', 0):.3f}s")
                
                # 检查结果
                if data.get('success'):
                    result = data.get('result', {})
                    print(f"结果类型: {result.get('type', 'UNKNOWN')}")
                    print(f"记录数: {result.get('record_count', 0)}")
                    print(f"数据源: {result.get('data_sources', [])}")
                    
                    # 检查证据包
                    evidence = data.get('evidence_package', {})
                    if evidence:
                        print(f"审计ID: {evidence.get('audit_id', 'N/A')}")
                        print(f"SQL查询: {'是' if evidence.get('sql_query') else '否'}")
                else:
                    print(f"❌ 查询失败: {data.get('error', 'Unknown error')}")
                    
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                print(f"响应: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求错误: {e}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析错误: {e}")
        except Exception as e:
            print(f"❌ 未知错误: {e}")
        
        print("-" * 30)
        time.sleep(1)  # 避免请求过快
    
    print("\n🎉 测试完成！")

def test_method_preferences():
    """测试方法偏好设置"""
    base_url = "http://localhost:8000/api/v1/data-processing/smart-query/"
    
    print("\n🔧 测试方法偏好设置")
    print("=" * 50)
    
    test_query = "What is the total budget for education?"
    methods = ["auto", "sql", "rag"]
    
    for method in methods:
        print(f"\n📝 测试方法偏好: {method.upper()}")
        
        try:
            response = requests.post(
                base_url,
                json={
                    "query": test_query,
                    "context": {},
                    "method_preference": method
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 查询成功")
                print(f"使用的方法: {data.get('method', 'UNKNOWN')}")
                print(f"置信度: {data.get('confidence_score', 0):.2f}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 错误: {e}")
        
        print("-" * 30)
        time.sleep(1)

if __name__ == "__main__":
    print("🚀 启动智能查询系统测试")
    
    # 等待服务器启动
    print("⏳ 等待服务器启动...")
    time.sleep(5)
    
    # 测试基本查询功能
    test_smart_query_system()
    
    # 测试方法偏好
    test_method_preferences()
    
    print("\n✨ 所有测试完成！")
