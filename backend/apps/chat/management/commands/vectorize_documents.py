"""
Django管理命令：文档向量化
用于将Finance/HR/Procurement记录转换为向量
"""

from django.core.management.base import BaseCommand
from apps.chat.rag_service import rag_service


class Command(BaseCommand):
    help = '将Finance/HR/Procurement记录转换为向量用于RAG检索'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制重建所有向量',
        )
        parser.add_argument(
            '--stats-only',
            action='store_true',
            help='只显示统计信息，不执行向量化',
        )

    def handle(self, *args, **options):
        force = options['force']
        stats_only = options['stats_only']

        if stats_only:
            self._show_vector_stats()
            return

        self.stdout.write(
            self.style.SUCCESS('开始文档向量化...')
        )

        try:
            # 执行向量化
            result = rag_service.vectorize_documents(force_rebuild=force)
            
            if result.get('success') is False:
                self.stdout.write(
                    self.style.ERROR(f'❌ 向量化失败: {result.get("error")}')
                )
                return
            
            # 显示结果
            self._display_vectorization_results(result)
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 向量化过程中出现错误: {str(e)}')
            )

    def _display_vectorization_results(self, result: dict):
        """显示向量化结果"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('🎯 向量化完成！'))
        self.stdout.write('='*50)
        
        # 统计信息
        self.stdout.write(f'\n📊 处理统计:')
        self.stdout.write(f'   💰 财务记录: {result.get("finance_records", 0)} 条')
        self.stdout.write(f'   👥 人力资源记录: {result.get("hr_records", 0)} 条')
        self.stdout.write(f'   📦 采购记录: {result.get("procurement_records", 0)} 条')
        self.stdout.write(f'   🔢 总向量数: {result.get("total_vectors", 0)} 个')
        
        # 错误信息
        errors = result.get('errors', [])
        if errors:
            self.stdout.write(f'\n⚠️  错误信息 ({len(errors)} 个):')
            for error in errors[:5]:  # 只显示前5个错误
                self.stdout.write(f'   • {error}')
            if len(errors) > 5:
                self.stdout.write(f'   ... 还有 {len(errors) - 5} 个错误')
        
        # 成功信息
        total_processed = (
            result.get("finance_records", 0) + 
            result.get("hr_records", 0) + 
            result.get("procurement_records", 0)
        )
        
        if total_processed > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ 成功处理 {total_processed} 条记录')
            )
            self.stdout.write(
                self.style.SUCCESS(f'✅ 生成了 {result.get("total_vectors", 0)} 个向量')
            )
        
        self.stdout.write('\n' + '='*50)

    def _show_vector_stats(self):
        """显示向量统计信息"""
        try:
            from apps.datasets.models import DocumentVector, FinanceRecord, HRRecord, ProcurementRecord
            
            total_vectors = DocumentVector.objects.count()
            finance_vectors = DocumentVector.objects.filter(source_table='finance_records').count()
            hr_vectors = DocumentVector.objects.filter(source_table='hr_records').count()
            procurement_vectors = DocumentVector.objects.filter(source_table='procurement_records').count()
            
            total_records = (
                FinanceRecord.objects.count() + 
                HRRecord.objects.count() + 
                ProcurementRecord.objects.count()
            )
            
            self.stdout.write('\n' + '='*50)
            self.stdout.write(self.style.SUCCESS('📊 向量统计信息'))
            self.stdout.write('='*50)
            
            self.stdout.write(f'\n📋 记录统计:')
            self.stdout.write(f'   💰 财务记录: {FinanceRecord.objects.count()} 条')
            self.stdout.write(f'   👥 人力资源记录: {HRRecord.objects.count()} 条')
            self.stdout.write(f'   📦 采购记录: {ProcurementRecord.objects.count()} 条')
            self.stdout.write(f'   🔢 总记录数: {total_records} 条')
            
            self.stdout.write(f'\n🔢 向量统计:')
            self.stdout.write(f'   💰 财务向量: {finance_vectors} 个')
            self.stdout.write(f'   👥 人力资源向量: {hr_vectors} 个')
            self.stdout.write(f'   📦 采购向量: {procurement_vectors} 个')
            self.stdout.write(f'   🔢 总向量数: {total_vectors} 个')
            
            # 覆盖率
            if total_records > 0:
                coverage = (total_vectors / total_records) * 100
                self.stdout.write(f'\n📈 向量化覆盖率: {coverage:.1f}%')
                
                if coverage < 100:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  建议运行向量化命令以提高覆盖率')
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ 所有记录都已向量化')
                    )
            
            self.stdout.write('\n' + '='*50)
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 获取统计信息失败: {str(e)}')
            )
