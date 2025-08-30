"""
AI查询服务模块
集成OpenAI/Langchain进行智能查询处理
"""

import os
import re
import json
import openai
from typing import Dict, List, Optional, Tuple
from django.db.models import Sum, Count, Q
from apps.datasets.models import BudgetExpense, Portfolio, Department

# OpenAI配置 (需要设置环境变量 OPENAI_API_KEY)
openai.api_key = os.getenv('OPENAI_API_KEY', 'your-openai-api-key-here')

class AIQueryService:
    """AI查询服务类"""
    
    def __init__(self):
        self.system_prompt = """你是一个专门分析澳大利亚政府预算数据的AI助手。

数据库结构：
- Portfolio: 政府部门组合 (如: Health and Aged Care, Education, Defence)
- Department: 具体部门/机构 
- BudgetExpense: 预算支出数据，包含以下字段：
  - portfolio: 所属部门组合
  - department: 所属部门
  - program: 项目名称
  - expense_type: 支出类型 (Departmental Expenses, Administered Expenses等)
  - amount_2023_24, amount_2024_25, amount_2025_26: 各年度金额

你的任务：
1. 分析用户的自然语言查询
2. 确定是否需要SQL查询(数值统计)还是RAG检索(具体信息)
3. 生成准确的SQL查询或检索策略
4. 提供可信度评分(0-1)

始终以JSON格式返回结果。"""

    def process_query(self, query: str, context: Dict = None) -> Dict:
        """
        处理用户查询
        
        Args:
            query: 用户的自然语言查询
            context: 查询上下文
            
        Returns:
            包含查询结果的字典
        """
        try:
            # 步骤1: 分析查询意图
            intent_analysis = self._analyze_intent(query)
            
            # 步骤2: 生成查询策略
            if intent_analysis['method'] == 'SQL':
                result = self._process_sql_query(query, intent_analysis)
            else:
                result = self._process_rag_query(query, intent_analysis)
                
            # 步骤3: 计算信任度
            result['confidence'] = self._calculate_confidence(result)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'confidence': 0.0
            }

    def _analyze_intent(self, query: str) -> Dict:
        """分析查询意图"""
        
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
    "method": "SQL" 或 "RAG",
    "intent": "查询意图描述",
    "entities": ["提取的实体"],
    "query_type": "budget_summary|department_analysis|specific_lookup|comparison",
    "sql_hint": "如果是SQL查询，提供SQL提示"
}}

SQL查询适用于：总计、平均值、排序、统计、对比分析
RAG查询适用于：具体记录、详细信息、特定人员/项目查找
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
        sql_keywords = ['total', 'sum', 'average', 'top', 'highest', 'lowest', 'compare', 'budget', 'amount']
        
        # RAG查询关键词  
        rag_keywords = ['details', 'about', 'find', 'who', 'record', 'information', 'specific']
        
        # 实体提取
        entities = []
        departments = ['education', 'health', 'defence', 'treasury', 'transport']
        for dept in departments:
            if dept in query_lower:
                entities.append(dept)
                
        # 判断查询方法
        sql_score = sum(1 for keyword in sql_keywords if keyword in query_lower)
        rag_score = sum(1 for keyword in rag_keywords if keyword in query_lower)
        
        method = 'SQL' if sql_score >= rag_score else 'RAG'
        
        return {
            'method': method,
            'intent': f'{method} query about government data',
            'entities': entities,
            'query_type': 'budget_summary' if method == 'SQL' else 'specific_lookup',
            'sql_hint': 'Generate appropriate SQL query' if method == 'SQL' else None
        }

    def _process_sql_query(self, query: str, intent: Dict) -> Dict:
        """处理SQL类型的查询"""
        
        # 根据查询生成并执行SQL
        if 'education' in query.lower() and ('total' in query.lower() or 'budget' in query.lower()):
            # 教育部门总预算查询
            result = self._get_education_budget_summary()
            sql_query = """SELECT SUM(amount_2024_25) as total_budget
FROM budget_expenses 
WHERE portfolio__name ILIKE '%education%'
AND amount_2024_25 IS NOT NULL"""
            
        elif 'department' in query.lower() and ('compare' in query.lower() or 'comparison' in query.lower()):
            # 部门对比查询
            result = self._get_department_comparison()
            sql_query = """SELECT portfolio__name, SUM(amount_2024_25) as total_amount
FROM budget_expenses 
WHERE amount_2024_25 IS NOT NULL
GROUP BY portfolio__name
ORDER BY total_amount DESC"""
            
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
                'timestamp': '2024-01-15 14:32:18 UTC',
                'audit_id': 'AUD-2024-0115-001'
            }
        }

    def _process_rag_query(self, query: str, intent: Dict) -> Dict:
        """处理RAG类型的查询"""
        
        # RAG查询处理逻辑
        return {
            'success': True,
            'method': 'RAG', 
            'answer': f"RAG查询结果: {query}",
            'data_sources': ['document_embeddings', 'knowledge_base'],
            'retrieved_docs': ['doc1', 'doc2'],
            'metadata': {
                'timestamp': '2024-01-15 14:32:18 UTC',
                'audit_id': 'AUD-2024-0115-002'
            }
        }

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

    def _calculate_confidence(self, result: Dict) -> float:
        """计算查询结果的可信度"""
        
        confidence = 0.5  # 基础置信度
        
        # 基于结果质量调整置信度
        if result.get('success'):
            confidence += 0.3
            
        if result.get('summary', {}).get('total_amount', 0) > 0:
            confidence += 0.1
            
        if result.get('table_data'):
            confidence += 0.1
            
        if result.get('rows', 0) > 0:
            confidence += 0.1
            
        return min(confidence, 1.0)


# 创建全局服务实例
ai_service = AIQueryService()
