from django.core.management.base import BaseCommand
from django.test import Client
from django.urls import reverse


class Command(BaseCommand):
    help = '测试Swagger API文档生成'

    def handle(self, *args, **options):
        self.stdout.write('🔍 测试Swagger API文档生成...')
        
        client = Client()
        
        # 测试API根路径
        try:
            self.stdout.write('📋 测试API根路径...')
            response = client.get('/api/')
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS('✅ API根路径正常'))
            else:
                self.stdout.write(self.style.ERROR(f'❌ API根路径失败: {response.status_code}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ API根路径异常: {str(e)}'))
        
        # 测试健康检查
        try:
            self.stdout.write('🏥 测试健康检查...')
            response = client.get('/api/health/')
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS('✅ 健康检查正常'))
            else:
                self.stdout.write(self.style.ERROR(f'❌ 健康检查失败: {response.status_code}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ 健康检查异常: {str(e)}'))
        
        # 测试OpenAPI schema生成
        try:
            self.stdout.write('📄 测试OpenAPI schema生成...')
            response = client.get('/api/schema/')
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS('✅ OpenAPI schema生成正常'))
                # 尝试解析JSON
                try:
                    import json
                    schema = json.loads(response.content.decode('utf-8'))
                    paths_count = len(schema.get('paths', {}))
                    self.stdout.write(f'   📊 发现 {paths_count} 个API端点')
                except json.JSONDecodeError:
                    self.stdout.write(self.style.WARNING('⚠️  Schema不是有效JSON'))
            else:
                self.stdout.write(self.style.ERROR(f'❌ Schema生成失败: {response.status_code}'))
                if hasattr(response, 'content'):
                    error_content = response.content.decode('utf-8')[:200]
                    self.stdout.write(f'   错误内容: {error_content}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Schema生成异常: {str(e)}'))
        
        # 测试Swagger UI
        try:
            self.stdout.write('🌐 测试Swagger UI...')
            response = client.get('/api/docs/')
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS('✅ Swagger UI正常'))
            else:
                self.stdout.write(self.style.ERROR(f'❌ Swagger UI失败: {response.status_code}'))
                if hasattr(response, 'content'):
                    error_content = response.content.decode('utf-8')[:200]
                    self.stdout.write(f'   错误内容: {error_content}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Swagger UI异常: {str(e)}'))
        
        # 测试数据集API
        try:
            self.stdout.write('📊 测试数据集API...')
            response = client.get('/api/v1/datasets/portfolios/')
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS('✅ 数据集API正常'))
            else:
                self.stdout.write(self.style.ERROR(f'❌ 数据集API失败: {response.status_code}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ 数据集API异常: {str(e)}'))
        
        self.stdout.write('')
        self.stdout.write('🎯 测试完成')
        self.stdout.write('如果所有测试都通过，API文档应该可以正常访问:')
        self.stdout.write('  http://localhost:8000/api/docs/')