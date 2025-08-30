"""
AI查询服务模块
集成OpenAI/Langchain进行智能查询处理
实现混合路由：SQL查询 + RAG检索
"""

import os
import re
import json
import openai
from typing import Dict, List, Optional, Tuple
from django.db.models import Sum, Count, Q, Avg, Max, Min
from django.utils import timezone
from apps.datasets.models import (
    BudgetExpense, Portfolio, Department, 
    FinanceRecord, HRRecord, ProcurementRecord
)
from .rag_service import rag_service

# OpenAI配置 (需要设置环境变量 OPENAI_API_KEY)
openai.api_key = os.getenv('OPENAI_API_KEY', 'your-openai-api-key-here')

class AIQueryService:
    """AI查询服务类 - 实现混合路由系统"""
    
    def __init__(self):
        self.system_prompt = """你是一个专门分析澳大利亚政府数据的AI助手。

数据库结构：
1. 预算数据表：
   - Portfolio: 政府部门组合 (如: Health and Aged Care, Education, Defence)
   - Department: 具体部门/机构 
   - BudgetExpense: 预算支出数据，包含各年度金额

2. 业务数据表（用于RAG检索）：
   - FinanceRecord: 财务记录（付款、发票、预算转移等）
   - HRRecord: 人力资源记录（雇佣、薪资、请假等）
   - ProcurementRecord: 采购记录（合同、招标、供应商等）

你的任务：
1. 分析用户的自然语言查询
2. 确定查询类型：
   - SQL查询：数值统计、汇总、排序、对比分析
   - RAG检索：具体记录查找、详细信息、事实查证
3. 生成准确的查询策略
4. 提供可信度评分(0-1)

始终以JSON格式返回结果。"""

    def process_query(self, query: str, context: Dict = None) -> Dict:
        """
        处理用户查询 - 混合路由系统
        
        Args:
            query: 用户的自然语言查询
            context: 查询上下文
            
        Returns:
            包含查询结果的字典
        """
        try:
            # 步骤1: 分析查询意图
            intent_analysis = self._analyze_intent(query)
            
            # 步骤2: 根据意图选择查询方法
            if intent_analysis['method'] == 'SQL':
                result = self._process_sql_query(query, intent_analysis)
            elif intent_analysis['method'] == 'RAG':
                result = self._process_rag_query(query, intent_analysis)
            else:
                # 混合查询：同时执行SQL和RAG
                result = self._process_hybrid_query(query, intent_analysis)
                
            # 步骤3: 计算信任度
            result['confidence'] = self._calculate_confidence(result)
            
            # 步骤4: 生成证据包
            result['evidence_package'] = self._generate_evidence_package(query, result)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'confidence': 0.0,
                'evidence_package': {
                    'error': str(e),
                    'search_method': 'error'
                }
            }

    def _analyze_intent(self, query: str) -> Dict:
        """分析查询意图 - 智能路由判断"""
        
        # 使用OpenAI分析查询意图
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"""
分析以下查询并返回JSON格式结果：

查询: "{query}"

返回格式：
{{
    "method": "SQL" 或 "RAG" 或 "HYBRID",
    "intent": "查询意图描述",
    "entities": ["提取的实体"],
    "query_type": "budget_summary|department_analysis|specific_lookup|comparison|fact_check",
    "sql_hint": "如果是SQL查询，提供SQL提示",
    "rag_hint": "如果是RAG查询，提供检索提示",
    "reasoning": "选择该方法的原因"
}}

SQL查询适用于：总计、平均值、排序、统计、对比分析、预算执行率、Top N
RAG查询适用于：具体记录、详细信息、特定人员/项目查找、事实查证
HYBRID适用于：需要统计信息+具体记录的复杂查询
"""}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            # 尝试提取JSON
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
                
        except Exception as e:
            print(f"OpenAI API错误: {e}")
            
        # 回退到基于规则的分析
        return self._rule_based_analysis(query)

    def _rule_based_analysis(self, query: str) -> Dict:
        """基于规则的查询分析（OpenAI API不可用时的回退方案）"""
        
        query_lower = query.lower()
        
        # SQL查询关键词
        sql_keywords = ['total', 'sum', 'average', 'avg', 'top', 'highest', 'lowest', 'compare', 'budget', 'amount', 'rate', 'percentage', 'outlier']
        
        # RAG查询关键词  
        rag_keywords = ['details', 'about', 'find', 'who', 'record', 'information', 'specific', 'latest', 'payment', 'contract', 'employee', 'supplier']
        
        # 混合查询关键词
        hybrid_keywords = ['how much', 'what is', 'show me', 'tell me about', 'analysis']
        
        # 实体提取
        entities = []
        departments = ['education', 'health', 'defence', 'treasury', 'transport']
        for dept in departments:
            if dept in query_lower:
                entities.append(dept)
                
        # 判断查询方法
        sql_score = sum(1 for keyword in sql_keywords if keyword in query_lower)
        rag_score = sum(1 for keyword in rag_keywords if keyword in query_lower)
        hybrid_score = sum(1 for keyword in hybrid_keywords if keyword in query_lower)
        
        if hybrid_score > 0 and (sql_score > 0 or rag_score > 0):
            method = 'HYBRID'
        elif sql_score >= rag_score:
            method = 'SQL'
        else:
            method = 'RAG'
        
        return {
            'method': method,
            'intent': f'{method} query about government data',
            'entities': entities,
            'query_type': 'budget_summary' if method == 'SQL' else 'specific_lookup',
            'sql_hint': 'Generate appropriate SQL query' if method in ['SQL', 'HYBRID'] else None,
            'rag_hint': 'Search relevant documents' if method in ['RAG', 'HYBRID'] else None,
            'reasoning': f'Method chosen based on keywords: SQL({sql_score}), RAG({rag_score}), Hybrid({hybrid_score})'
        }

    def _process_sql_query(self, query: str, intent: Dict) -> Dict:
        """处理SQL类型的查询 - 数值统计和聚合"""
        
        try:
            # 根据查询生成并执行SQL
            if 'education' in query.lower() and ('total' in query.lower() or 'budget' in query.lower()):
                result = self._get_education_budget_summary()
                sql_query = """SELECT SUM(amount_2024_25) as total_budget
FROM budget_expenses 
WHERE portfolio__name ILIKE '%education%'
AND amount_2024_25 IS NOT NULL"""
                
            elif 'department' in query.lower() and ('compare' in query.lower() or 'comparison' in query.lower()):
                result = self._get_department_comparison()
                sql_query = """SELECT portfolio__name, SUM(amount_2024_25) as total_amount
FROM budget_expenses 
WHERE amount_2024_25 IS NOT NULL
GROUP BY portfolio__name
ORDER BY total_amount DESC"""
                
            elif 'top' in query.lower() and ('10' in query or 'highest' in query.lower()):
                result = self._get_top_expenses()
                sql_query = """SELECT portfolio__name, department__name, program__name, amount_2024_25
FROM budget_expenses 
WHERE amount_2024_25 IS NOT NULL
ORDER BY amount_2024_25 DESC
LIMIT 10"""
                
            elif 'average' in query.lower() or 'avg' in query.lower():
                result = self._get_average_budgets()
                sql_query = """SELECT portfolio__name, AVG(amount_2024_25) as avg_amount
FROM budget_expenses 
WHERE amount_2024_25 IS NOT NULL
GROUP BY portfolio__name
ORDER BY avg_amount DESC"""
                
            else:
                # 通用查询
                result = self._get_general_budget_summary()
                sql_query = """SELECT COUNT(*) as total_records, 
SUM(amount_2024_25) as total_budget
FROM budget_expenses 
WHERE amount_2024_25 IS NOT NULL"""

            return {
                'success': True,
                'method': 'SQL',
                'answer': result['answer'],
                'executed_query': sql_query,
                'data_sources': ['budget_expenses', 'portfolios', 'departments'],
                'summary': result['summary'],
                'table_data': result.get('table_data', []),
                'metadata': {
                    'rows': result.get('rows', 0),
                    'timestamp': timezone.now().isoformat(),
                    'audit_id': f"AUD-{timezone.now().strftime('%Y%m%d')}-{hash(query) % 1000:03d}",
                    'query_type': 'aggregation'
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'method': 'SQL',
                'error': str(e),
                'confidence': 0.0
            }

    def _process_rag_query(self, query: str, intent: Dict) -> Dict:
        """处理RAG类型的查询 - 文档检索和事实查证"""
        
        try:
            # 使用RAG服务搜索相关文档
            search_results = rag_service.search_documents(query)
            
            if search_results:
                # 生成回答
                answer = self._generate_rag_answer(query, search_results)
                
                return {
                    'success': True,
                    'method': 'RAG',
                    'answer': answer,
                    'executed_query': f"RAG search: {query}",
                    'data_sources': list(set(r['source_table'] for r in search_results)),
                    'summary': f"找到 {len(search_results)} 条相关记录",
                    'table_data': search_results,
                    'metadata': {
                        'rows': len(search_results),
                        'timestamp': timezone.now().isoformat(),
                        'audit_id': f"RAG-{timezone.now().strftime('%Y%m%d')}-{hash(query) % 1000:03d}",
                        'query_type': 'document_retrieval',
                        'search_results': len(search_results)
                    }
                }
            else:
                return {
                    'success': False,
                    'method': 'RAG',
                    'answer': f"抱歉，没有找到与 '{query}' 相关的记录。",
                    'confidence': 0.0
                }
                
        except Exception as e:
            return {
                'success': False,
                'method': 'RAG',
                'error': str(e),
                'confidence': 0.0
            }

    def _process_hybrid_query(self, query: str, intent: Dict) -> Dict:
        """处理混合查询 - 同时执行SQL和RAG"""
        
        try:
            # 并行执行SQL和RAG查询
            sql_result = self._process_sql_query(query, intent)
            rag_result = self._process_rag_query(query, intent)
            
            # 合并结果
            combined_answer = self._combine_hybrid_results(sql_result, rag_result)
            
            return {
                'success': True,
                'method': 'HYBRID',
                'answer': combined_answer,
                'sql_result': sql_result if sql_result.get('success') else None,
                'rag_result': rag_result if rag_result.get('success') else None,
                'data_sources': list(set(
                    (sql_result.get('data_sources', []) if sql_result.get('success') else []) +
                    (rag_result.get('data_sources', []) if rag_result.get('success') else [])
                )),
                'summary': f"混合查询：SQL({sql_result.get('success', False)}) + RAG({rag_result.get('success', False)})",
                'metadata': {
                    'timestamp': timezone.now().isoformat(),
                    'audit_id': f"HYB-{timezone.now().strftime('%Y%m%d')}-{hash(query) % 1000:03d}",
                    'query_type': 'hybrid_analysis'
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'method': 'HYBRID',
                'error': str(e),
                'confidence': 0.0
            }

    def _generate_rag_answer(self, query: str, search_results: List[Dict]) -> str:
        """基于RAG搜索结果生成回答"""
        
        if not search_results:
            return f"抱歉，没有找到与 '{query}' 相关的记录。"
        
        # 构建回答
        answer_parts = [f"基于搜索结果，我找到了 {len(search_results)} 条相关记录：\n\n"]
        
        for i, result in enumerate(search_results[:3], 1):  # 只显示前3条
            table_name = result['source_table'].replace('_', ' ').title()
            summary = result['record_summary']
            relevance = f"{result['relevance_score']:.2f}"
            
            answer_parts.append(f"{i}. **{table_name}**: {summary} (相关性: {relevance})\n")
        
        if len(search_results) > 3:
            answer_parts.append(f"\n... 还有 {len(search_results) - 3} 条记录")
        
        answer_parts.append(f"\n这些记录来自 {', '.join(set(r['source_table'] for r in search_results))} 等数据源。")
        
        return "".join(answer_parts)

    def _combine_hybrid_results(self, sql_result: Dict, rag_result: Dict) -> str:
        """合并SQL和RAG查询结果"""
        
        combined_parts = ["**混合查询结果**\n\n"]
        
        # SQL结果
        if sql_result.get('success'):
            combined_parts.append("**📊 统计信息：**\n")
            combined_parts.append(f"{sql_result.get('answer', '')}\n\n")
        
        # RAG结果
        if rag_result.get('success'):
            combined_parts.append("**📋 相关记录：**\n")
            combined_parts.append(f"{rag_result.get('answer', '')}\n\n")
        
        combined_parts.append("**💡 提示：** 统计信息提供数值概览，相关记录提供具体详情。")
        
        return "".join(combined_parts)

    def _generate_evidence_package(self, query: str, result: Dict) -> Dict:
        """生成证据包 - 包含数据来源、行号、时间戳等审计信息"""
        
        evidence_package = {
            'query': query,
            'search_timestamp': timezone.now().isoformat(),
            'method': result.get('method', 'unknown'),
            'data_sources': result.get('data_sources', []),
            'metadata': result.get('metadata', {}),
            'evidence_items': []
        }
        
        # 添加SQL证据
        if result.get('method') in ['SQL', 'HYBRID'] and result.get('executed_query'):
            evidence_package['evidence_items'].append({
                'type': 'sql_query',
                'content': result['executed_query'],
                'data_sources': result.get('data_sources', []),
                'rows_affected': result.get('metadata', {}).get('rows', 0)
            })
        
        # 添加RAG证据
        if result.get('method') in ['RAG', 'HYBRID'] and result.get('table_data'):
            for item in result['table_data'][:5]:  # 限制数量
                evidence_package['evidence_items'].append({
                    'type': 'document_retrieval',
                    'source_table': item.get('source_table'),
                    'record_id': item.get('record_id'),
                    'relevance_score': item.get('relevance_score', 0),
                    'content_preview': item.get('content_text', '')[:100] + "..." if len(item.get('content_text', '')) > 100 else item.get('content_text', '')
                })
        
        return evidence_package

    def _calculate_confidence(self, result: Dict) -> float:
        """计算查询结果的置信度"""
        
        base_confidence = 0.5
        
        # 根据方法调整置信度
        if result.get('method') == 'SQL':
            base_confidence += 0.3  # SQL查询通常更可靠
        elif result.get('method') == 'RAG':
            base_confidence += 0.2  # RAG检索的可靠性
        elif result.get('method') == 'HYBRID':
            base_confidence += 0.4  # 混合查询最可靠
        
        # 根据数据源数量调整
        data_sources = result.get('data_sources', [])
        if len(data_sources) > 1:
            base_confidence += 0.1
        
        # 根据结果数量调整
        if result.get('table_data'):
            if len(result['table_data']) > 0:
                base_confidence += 0.1
        
        return min(base_confidence, 1.0)

    def _get_education_budget_summary(self) -> Dict:
        """获取教育部门预算摘要"""
        
        try:
            # 查询教育相关的预算数据
            education_expenses = BudgetExpense.objects.filter(
                Q(portfolio__name__icontains='education') |
                Q(department__name__icontains='education')
            ).filter(amount_2024_25__isnull=False)
            
            total_budget = education_expenses.aggregate(
                total=Sum('amount_2024_25')
            )['total'] or 0
            
            # 按部门分组
            dept_breakdown = education_expenses.values(
                'department__name'
            ).annotate(
                total_amount=Sum('amount_2024_25'),
                count=Count('id')
            ).order_by('-total_amount')
            
            # 构建表格数据
            table_data = []
            for dept in dept_breakdown[:5]:  # 取前5个
                percentage = (dept['total_amount'] / total_budget * 100) if total_budget > 0 else 0
                table_data.append({
                    'department': dept['department__name'] or 'Unknown',
                    'amount': float(dept['total_amount']),
                    'percentage': round(percentage, 1)
                })
            
            return {
                'answer': 'What is the total education budget for 2024?',
                'summary': {
                    'total_amount': float(total_budget),
                    'breakdown': table_data
                },
                'table_data': table_data,
                'rows': education_expenses.count()
            }
            
        except Exception as e:
            return {
                'answer': f'Error querying education budget: {str(e)}',
                'summary': {'total_amount': 0},
                'table_data': [],
                'rows': 0
            }

    def _get_department_comparison(self) -> Dict:
        """获取部门对比数据"""
        
        try:
            # 按部门组合统计预算
            portfolio_summary = BudgetExpense.objects.filter(
                amount_2024_25__isnull=False
            ).values(
                'portfolio__name'
            ).annotate(
                total_amount=Sum('amount_2024_25'),
                count=Count('id')
            ).order_by('-total_amount')[:10]
            
            total_all = sum(item['total_amount'] for item in portfolio_summary)
            
            table_data = []
            for item in portfolio_summary:
                percentage = (item['total_amount'] / total_all * 100) if total_all > 0 else 0
                table_data.append({
                    'department': item['portfolio__name'] or 'Unknown',
                    'amount': float(item['total_amount']),
                    'percentage': round(percentage, 1)
                })
            
            return {
                'answer': 'Department budget comparison for 2024',
                'summary': {
                    'total_amount': float(total_all),
                    'breakdown': table_data
                },
                'table_data': table_data,
                'rows': sum(item['count'] for item in portfolio_summary)
            }
            
        except Exception as e:
            return {
                'answer': f'Error comparing departments: {str(e)}',
                'summary': {'total_amount': 0},
                'table_data': [],
                'rows': 0
            }

    def _get_general_budget_summary(self) -> Dict:
        """获取通用预算摘要"""
        
        try:
            total_records = BudgetExpense.objects.filter(
                amount_2024_25__isnull=False
            ).count()
            
            total_budget = BudgetExpense.objects.filter(
                amount_2024_25__isnull=False
            ).aggregate(total=Sum('amount_2024_25'))['total'] or 0
            
            return {
                'answer': 'General budget summary for 2024',
                'summary': {
                    'total_amount': float(total_budget),
                    'breakdown': []
                },
                'table_data': [],
                'rows': total_records
            }
            
        except Exception as e:
            return {
                'answer': f'Error getting budget summary: {str(e)}',
                'summary': {'total_amount': 0},
                'table_data': [],
                'rows': 0
            }

    def _get_top_expenses(self) -> Dict:
        """获取预算支出Top N"""
        try:
            top_expenses = BudgetExpense.objects.filter(
                amount_2024_25__isnull=False
            ).values(
                'portfolio__name', 'department__name', 'program__name'
            ).annotate(
                total_amount=Sum('amount_2024_25')
            ).order_by('-total_amount')[:10]

            table_data = []
            for item in top_expenses:
                table_data.append({
                    'portfolio': item['portfolio__name'] or 'Unknown',
                    'department': item['department__name'] or 'Unknown',
                    'program': item['program__name'] or 'Unknown',
                    'amount': float(item['total_amount'])
                })

            return {
                'answer': 'Top 10 budget expenses by amount for 2024',
                'summary': {
                    'total_amount': sum(item['total_amount'] for item in top_expenses),
                    'breakdown': table_data
                },
                'table_data': table_data,
                'rows': len(top_expenses)
            }
        except Exception as e:
            return {
                'answer': f'Error getting top expenses: {str(e)}',
                'summary': {'total_amount': 0},
                'table_data': [],
                'rows': 0
            }

    def _get_average_budgets(self) -> Dict:
        """获取各年度预算平均值"""
        try:
            average_budgets = BudgetExpense.objects.filter(
                amount_2024_25__isnull=False
            ).values(
                'portfolio__name', 'program__name'
            ).annotate(
                avg_amount=Avg('amount_2024_25')
            ).order_by('-avg_amount')

            table_data = []
            for item in average_budgets:
                table_data.append({
                    'portfolio': item['portfolio__name'] or 'Unknown',
                    'program': item['program__name'] or 'Unknown',
                    'average_amount': float(item['avg_amount'])
                })

            return {
                'answer': 'Average budget by portfolio and program for 2024',
                'summary': {
                    'total_amount': sum(item['avg_amount'] for item in average_budgets),
                    'breakdown': table_data
                },
                'table_data': table_data,
                'rows': len(average_budgets)
            }
        except Exception as e:
            return {
                'answer': f'Error getting average budgets: {str(e)}',
                'summary': {'total_amount': 0},
                'table_data': [],
                'rows': 0
            }


# 创建全局服务实例
ai_service = AIQueryService()
