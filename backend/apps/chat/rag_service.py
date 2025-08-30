"""
RAG (Retrieval-Augmented Generation) 服务模块
用于文档向量化、存储和检索
"""

import hashlib
import json
import numpy as np
from typing import Dict, List, Optional, Tuple
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from apps.datasets.models import (
    FinanceRecord, HRRecord, ProcurementRecord, DocumentVector
)

class RAGService:
    """RAG服务类 - 处理文档向量化和检索"""
    
    def __init__(self):
        self.chunk_size = 1000  # 文档分块大小
        self.overlap = 200      # 分块重叠大小
        self.top_k = 5          # 检索结果数量
        
    def vectorize_documents(self, force_rebuild: bool = False) -> Dict:
        """
        将 Finance/HR/Procurement 记录转换为向量
        
        Args:
            force_rebuild: 是否强制重建所有向量
            
        Returns:
            向量化结果统计
        """
        try:
            stats = {
                'finance_records': 0,
                'hr_records': 0,
                'procurement_records': 0,
                'total_vectors': 0,
                'errors': []
            }
            
            # 1. 处理财务记录
            if force_rebuild:
                DocumentVector.objects.filter(source_table='finance_records').delete()
            
            finance_records = FinanceRecord.objects.all()
            for record in finance_records:
                try:
                    self._vectorize_finance_record(record)
                    stats['finance_records'] += 1
                except Exception as e:
                    stats['errors'].append(f"Finance record {record.id}: {str(e)}")
            
            # 2. 处理人力资源记录
            if force_rebuild:
                DocumentVector.objects.filter(source_table='hr_records').delete()
                
            hr_records = HRRecord.objects.all()
            for record in hr_records:
                try:
                    self._vectorize_hr_record(record)
                    stats['hr_records'] += 1
                except Exception as e:
                    stats['errors'].append(f"HR record {record.id}: {str(e)}")
            
            # 3. 处理采购记录
            if force_rebuild:
                DocumentVector.objects.filter(source_table='procurement_records').delete()
                
            procurement_records = ProcurementRecord.objects.all()
            for record in procurement_records:
                try:
                    self._vectorize_procurement_record(record)
                    stats['procurement_records'] += 1
                except Exception as e:
                    stats['errors'].append(f"Procurement record {record.id}: {str(e)}")
            
            stats['total_vectors'] = DocumentVector.objects.count()
            return stats
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'stats': stats
            }
    
    def _vectorize_finance_record(self, record: FinanceRecord):
        """向量化财务记录"""
        # 构建文档文本
        content_parts = [
            f"财务记录类型: {record.get_record_type_display()}",
            f"部门: {record.department.name}",
            f"金额: {record.amount} {record.currency}",
            f"交易日期: {record.transaction_date}",
            f"参考编号: {record.reference_number}",
            f"描述: {record.description}",
            f"供应商: {record.supplier_name}" if record.supplier_name else "",
            f"账户代码: {record.account_code}" if record.account_code else "",
            f"状态: {record.status}",
            f"审批状态: {record.approval_status}"
        ]
        
        content_text = " | ".join([part for part in content_parts if part])
        content_hash = hashlib.sha256(content_text.encode()).hexdigest()
        
        # 检查是否已存在
        if DocumentVector.objects.filter(content_hash=content_hash).exists():
            return
        
        # 创建向量记录
        content_type = ContentType.objects.get_for_model(FinanceRecord)
        DocumentVector.objects.create(
            content_type=content_type,
            object_id=record.id,
            content_hash=content_hash,
            content_text=content_text,
            vector_embedding=self._generate_simple_embedding(content_text),
            source_table='finance_records',
            record_id=str(record.id)
        )
    
    def _vectorize_hr_record(self, record: HRRecord):
        """向量化人力资源记录"""
        content_parts = [
            f"人力资源记录类型: {record.get_record_type_display()}",
            f"部门: {record.department.name}",
            f"员工ID: {record.employee_id}",
            f"员工姓名: {record.employee_name}",
            f"职位: {record.position}",
            f"雇佣类型: {record.employment_type}",
            f"描述: {record.description}",
            f"开始日期: {record.start_date}",
            f"结束日期: {record.end_date}" if record.end_date else "",
            f"金额: {record.amount}" if record.amount else "",
            f"天数: {record.days}" if record.days else "",
            f"状态: {record.status}",
            f"审批状态: {record.approval_status}"
        ]
        
        content_text = " | ".join([part for part in content_parts if part])
        content_hash = hashlib.sha256(content_text.encode()).hexdigest()
        
        if DocumentVector.objects.filter(content_hash=content_hash).exists():
            return
        
        content_type = ContentType.objects.get_for_model(HRRecord)
        DocumentVector.objects.create(
            content_type=content_type,
            object_id=record.id,
            content_hash=content_hash,
            content_text=content_text,
            vector_embedding=self._generate_simple_embedding(content_text),
            source_table='hr_records',
            record_id=str(record.id)
        )
    
    def _vectorize_procurement_record(self, record: ProcurementRecord):
        """向量化采购记录"""
        content_parts = [
            f"采购记录类型: {record.get_record_type_display()}",
            f"部门: {record.department.name}",
            f"合同编号: {record.contract_number}",
            f"供应商名称: {record.supplier_name}",
            f"供应商ABN: {record.supplier_abn}" if record.supplier_abn else "",
            f"描述: {record.description}",
            f"合同价值: {record.contract_value}",
            f"开始日期: {record.start_date}",
            f"结束日期: {record.end_date}",
            f"采购类别: {record.category}",
            f"子类别: {record.subcategory}" if record.subcategory else "",
            f"状态: {record.status}",
            f"审批状态: {record.approval_status}"
        ]
        
        content_text = " | ".join([part for part in content_parts if part])
        content_hash = hashlib.sha256(content_text.encode()).hexdigest()
        
        if DocumentVector.objects.filter(content_hash=content_hash).exists():
            return
        
        content_type = ContentType.objects.get_for_model(ProcurementRecord)
        DocumentVector.objects.create(
            content_type=content_type,
            object_id=record.id,
            content_hash=content_hash,
            content_text=content_text,
            vector_embedding=self._generate_simple_embedding(content_text),
            source_table='procurement_records',
            record_id=str(record.id)
        )
    
    def _generate_simple_embedding(self, text: str) -> List[float]:
        """
        生成简单的文本向量表示
        注意：这是一个简化的实现，生产环境应使用专业的向量模型
        """
        # 简单的TF-IDF风格向量化
        words = text.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 2:  # 过滤短词
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # 生成固定长度的向量（这里使用100维）
        vector = [0.0] * 100
        for i, (word, freq) in enumerate(word_freq.items()):
            if i < 100:
                vector[i] = freq / len(words)
        
        return vector
    
    def search_documents(self, query: str, table_filter: str = None) -> List[Dict]:
        """
        搜索相关文档
        
        Args:
            query: 搜索查询
            table_filter: 表过滤器 (finance_records, hr_records, procurement_records)
            
        Returns:
            相关文档列表
        """
        try:
            # 构建查询条件
            q_objects = Q()
            if table_filter:
                q_objects &= Q(source_table=table_filter)
            
            # 简单的关键词匹配（生产环境应使用向量相似度搜索）
            query_words = query.lower().split()
            for word in query_words:
                if len(word) > 2:
                    q_objects |= Q(content_text__icontains=word)
            
            # 执行搜索
            vectors = DocumentVector.objects.filter(q_objects).order_by('-created_at')[:self.top_k]
            
            results = []
            for vector in vectors:
                # 获取原始记录
                try:
                    record = self._get_record_from_vector(vector)
                    if record:
                        results.append({
                            'id': str(vector.id),
                            'source_table': vector.source_table,
                            'record_id': vector.record_id,
                            'content_text': vector.content_text,
                            'relevance_score': self._calculate_relevance(query, vector.content_text),
                            'record_data': record,
                            'metadata': {
                                'created_at': vector.created_at.isoformat(),
                                'content_hash': vector.content_hash
                            }
                        })
                except Exception as e:
                    continue
            
            # 按相关性排序
            results.sort(key=lambda x: x['relevance_score'], reverse=True)
            return results
            
        except Exception as e:
            return []
    
    def _get_record_from_vector(self, vector: DocumentVector):
        """从向量获取原始记录"""
        try:
            if vector.source_table == 'finance_records':
                return FinanceRecord.objects.get(id=vector.record_id)
            elif vector.source_table == 'hr_records':
                return HRRecord.objects.get(id=vector.record_id)
            elif vector.source_table == 'procurement_records':
                return ProcurementRecord.objects.get(id=vector.record_id)
        except:
            return None
    
    def _calculate_relevance(self, query: str, content: str) -> float:
        """计算查询与内容的相关性分数"""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        if not query_words or not content_words:
            return 0.0
        
        intersection = query_words & content_words
        union = query_words | content_words
        
        # Jaccard相似度
        jaccard = len(intersection) / len(union) if union else 0.0
        
        # 关键词密度
        keyword_density = len(intersection) / len(content_words) if content_words else 0.0
        
        # 综合分数
        relevance = (jaccard * 0.6) + (keyword_density * 0.4)
        return min(relevance, 1.0)
    
    def get_evidence_package(self, query: str, results: List[Dict]) -> Dict:
        """
        生成证据包
        
        Args:
            query: 原始查询
            results: 搜索结果
            
        Returns:
            证据包信息
        """
        evidence_package = {
            'query': query,
            'search_timestamp': None,
            'total_results': len(results),
            'data_sources': [],
            'evidence_items': [],
            'metadata': {
                'search_method': 'RAG',
                'vector_count': DocumentVector.objects.count(),
                'tables_searched': list(set(r['source_table'] for r in results))
            }
        }
        
        for result in results:
            evidence_item = {
                'source_table': result['source_table'],
                'record_id': result['record_id'],
                'relevance_score': result['relevance_score'],
                'content_preview': result['content_text'][:200] + "..." if len(result['content_text']) > 200 else result['content_text'],
                'record_summary': self._generate_record_summary(result['record_data']),
                'metadata': result['metadata']
            }
            evidence_package['evidence_items'].append(evidence_item)
            
            if result['source_table'] not in evidence_package['data_sources']:
                evidence_package['data_sources'].append(result['source_table'])
        
        return evidence_package
    
    def _generate_record_summary(self, record) -> str:
        """生成记录摘要"""
        if hasattr(record, 'reference_number'):  # FinanceRecord
            return f"{record.get_record_type_display()} - {record.reference_number} - {record.amount}"
        elif hasattr(record, 'employee_name'):  # HRRecord
            return f"{record.get_record_type_display()} - {record.employee_name} - {record.position}"
        elif hasattr(record, 'contract_number'):  # ProcurementRecord
            return f"{record.get_record_type_display()} - {record.contract_number} - {record.supplier_name}"
        else:
            return str(record)


# 全局RAG服务实例
rag_service = RAGService()
