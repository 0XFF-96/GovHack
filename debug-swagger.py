#!/usr/bin/env python3

"""
简单的Swagger调试脚本
用于测试API文档是否可以正常生成
"""

import requests
import json
import sys

def test_endpoints():
    base_url = "http://localhost:8000"
    
    endpoints_to_test = [
        "/api/health/",
        "/api/",
        "/api/schema/", 
        "/api/docs/",
    ]
    
    print("🔍 测试API端点...")
    print("=" * 50)
    
    for endpoint in endpoints_to_test:
        url = base_url + endpoint
        try:
            print(f"📋 测试: {endpoint}")
            response = requests.get(url, timeout=10)
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ 成功")
                if endpoint == "/api/schema/":
                    # 检查schema内容
                    try:
                        schema = response.json()
                        if 'openapi' in schema:
                            print(f"   📄 OpenAPI版本: {schema.get('openapi')}")
                            print(f"   📋 API标题: {schema.get('info', {}).get('title')}")
                            paths_count = len(schema.get('paths', {}))
                            print(f"   🔗 端点数量: {paths_count}")
                        else:
                            print("   ⚠️  Schema格式异常")
                    except json.JSONDecodeError:
                        print("   ⚠️  Schema不是有效JSON")
            elif response.status_code == 302:
                print(f"   🔄 重定向到: {response.headers.get('Location')}")
            else:
                print(f"   ❌ 失败: {response.status_code}")
                if response.text:
                    print(f"   错误信息: {response.text[:200]}")
                    
        except requests.exceptions.RequestException as e:
            print(f"   ❌ 连接错误: {str(e)}")
        except Exception as e:
            print(f"   ❌ 未知错误: {str(e)}")
        
        print()

if __name__ == "__main__":
    print("🐍 Swagger调试工具")
    print("请确保开发服务器正在运行 (./start.sh dev)")
    print()
    
    test_endpoints()
    
    print("🎯 如果所有测试都成功，API文档应该可以正常访问")
    print("   访问: http://localhost:8000/api/docs/")