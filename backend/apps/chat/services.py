"""
OpenRouter AI Service for Government Data Chatbot

This service provides integration with OpenRouter AI for generating accurate,
trustworthy responses to government data queries.
"""
import os
import json
import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

import requests
from django.conf import settings
from django.core.cache import cache
from django.db import models

logger = logging.getLogger(__name__)


@dataclass
class AIResponse:
    """AI response data structure"""
    content: str
    trust_score: float
    processing_time: float
    data_sources: List[str]
    intent: str
    entities: Dict[str, str]
    model_used: str


class GovernmentDataRetriever:
    """Service for retrieving relevant government data based on user queries"""
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes
    
    def _get_models(self):
        """Lazy import of Django models to avoid import issues"""
        try:
            from apps.datasets.models import BudgetExpense, Portfolio, Department
            return BudgetExpense, Portfolio, Department
        except ImportError as e:
            logger.error(f"Error importing models: {e}")
            return None, None, None
    
    def extract_intent_and_entities(self, query: str) -> Tuple[str, Dict[str, str]]:
        """Extract intent and entities from user query - ENHANCED FOR DASHBOARD QUERIES"""
        query_lower = query.lower()
        entities = {}
        intent = "general_inquiry"
        
        # Dashboard-specific intents (HIGH PRIORITY)
        if any(word in query_lower for word in ['dashboard', 'overview', 'summary', 'total', 'show me']):
            intent = "dashboard_inquiry"
            
        # Budget-related intents
        if any(word in query_lower for word in ['budget', 'spending', 'allocation', 'money', 'cost', 'expense', 'financial']):
            if intent == "general_inquiry":
                intent = "budget_inquiry"
            
        # Portfolio-specific queries  
        if any(word in query_lower for word in ['portfolio', 'portfolios', 'top portfolio', 'largest portfolio', 'biggest portfolio']):
            intent = "portfolio_inquiry"
            
        # Ranking/comparison queries (dashboard-style)
        if any(word in query_lower for word in ['top', 'largest', 'biggest', 'highest', 'ranking', 'list', 'compare', 'comparison', 'vs', 'versus']):
            intent = "ranking_query"
            
        # Breakdown/analysis queries (dashboard-style)
        if any(word in query_lower for word in ['breakdown', 'analysis', 'distribution', 'categories', 'types', 'how much']):
            intent = "breakdown_query"
            
        # Trends/historical analysis
        if any(word in query_lower for word in ['trends', 'change', 'growth', 'over time', 'historical', 'year over year', 'previous year']):
            intent = "comparison_query"
            
        # Amount-related queries
        if any(word in query_lower for word in ['how much', 'total', 'amount', 'value', 'spend', 'cost']):
            if intent == "general_inquiry":
                intent = "amount_query"
            
        # Department-specific queries
        departments = [
            'health', 'education', 'defence', 'defense', 'treasury', 'social services',
            'infrastructure', 'agriculture', 'environment', 'home affairs',
            'finance', 'foreign affairs', 'industry', 'communications',
            'attorney general', 'prime minister', 'immigration'
        ]
        for dept in departments:
            if dept in query_lower:
                entities['department'] = dept
                if intent == "general_inquiry":
                    intent = "department_inquiry"
        
        # Portfolio extraction (enhanced)
        portfolios = [
            'health and aged care', 'education', 'defence', 'treasury',
            'social services', 'infrastructure', 'agriculture',
            'environment', 'home affairs', 'attorney general'
        ]
        for portfolio in portfolios:
            if portfolio in query_lower:
                entities['portfolio'] = portfolio
                if intent == "general_inquiry":
                    intent = "portfolio_inquiry"
                    
        # Year extraction (enhanced for fiscal years)
        fiscal_years = ['2024-25', '2023-24', '2025-26', '2022-23', '2026-27', '2027-28']
        for fy in fiscal_years:
            if fy in query or fy.replace('-', '') in query:
                entities['fiscal_year'] = fy
                
        # Individual year extraction
        years = ['2024', '2023', '2022', '2021', '2020', '2025', '2026', '2027', '2028']
        for year in years:
            if year in query:
                if int(year) >= 2023:
                    entities['fiscal_year'] = f"{year}-{str(int(year)+1)[2:]}"
                    
        # Program/service keywords
        programs = ['medicare', 'ndis', 'jobseeker', 'aged care', 'childcare', 'university', 'hospital']
        for program in programs:
            if program in query_lower:
                entities['program'] = program
                if intent == "general_inquiry":
                    intent = "program_inquiry"
                    
        return intent, entities
    
    def get_relevant_data(self, intent: str, entities: Dict[str, str]) -> Dict:
        """Retrieve relevant government data based on intent and entities - EXACT SAME AS DASHBOARD"""
        # DISABLE CACHE FOR DEBUGGING
        # cache_key = f"gov_data_{intent}_{hash(str(entities))}"
        # cached_data = cache.get(cache_key)
        # 
        # if cached_data:
        #     return cached_data
            
        data = {
            'budget_records': [],
            'portfolios': [],
            'departments': [],
            'summary_stats': {},
            'top_portfolios': [],
            'expense_breakdown': [],
            'dashboard_metrics': {},  # New: Dashboard-specific metrics
            'trends_data': []  # New: Trends data same as dashboard
        }
        
        try:
            # Get models with lazy import
            BudgetExpense, Portfolio, Department = self._get_models()
            
            if not BudgetExpense:
                logger.warning("Models not available, returning empty data")
                return data
            
            from django.db.models import Sum, Count, Q
            
            # EXACT DASHBOARD DATA REPLICATION
            
            # 1. Budget Summary (same as /api/v1/datasets/budget/summary/)
            fiscal_year = entities.get('fiscal_year', '2024-25')
            amount_field = f'amount_{fiscal_year.replace("-", "_")}'
            
            logger.info(f"Chat Service: Retrieving data for fiscal year {fiscal_year}, field: {amount_field}")
            
            # Calculate basic budget statistics for fiscal year (EXACT DASHBOARD LOGIC)
            basic_stats = BudgetExpense.objects.filter(
                **{f'{amount_field}__isnull': False}
            ).aggregate(
                total_budget=Sum(amount_field),
                expense_count=Count('id'),
                portfolio_count=Count('portfolio', distinct=True),
                department_count=Count('department', distinct=True),
                program_count=Count('program', distinct=True)
            )
            
            logger.info(f"Chat Service: Basic stats - {basic_stats}")
            
            # 2. Top Portfolios (EXACT DASHBOARD LOGIC from budget_summary view)
            # Use the exact same query as the budget_summary API endpoint
            top_portfolios_query = Portfolio.objects.filter(
                budgetexpense__amount_2024_25__isnull=False
            ).annotate(
                total_amount=Sum('budgetexpense__amount_2024_25')
            ).order_by('-total_amount')[:10]
            
            logger.info(f"Chat Service: Portfolio query executed, found {top_portfolios_query.count()} portfolios")
            
            top_portfolios_data = []
            for p in top_portfolios_query:
                portfolio_data = {
                    'name': p.name,
                    'amount': float(p.total_amount or 0)
                }
                top_portfolios_data.append(portfolio_data)
                logger.info(f"  Top Portfolio: {p.name} - ${p.total_amount:,.0f}")
            
            data['top_portfolios'] = top_portfolios_data
            
            # 3. Expense Breakdown (EXACT DASHBOARD LOGIC)
            expense_breakdown_query = BudgetExpense.objects.filter(
                amount_2024_25__isnull=False
            ).values('expense_type').annotate(
                total_amount=Sum('amount_2024_25'),
                count=Count('id')
            ).order_by('-total_amount')
            
            expense_breakdown_data = [
                {
                    'type': item['expense_type'],
                    'amount': float(item['total_amount'] or 0),
                    'count': item['count']
                }
                for item in expense_breakdown_query
            ]
            data['expense_breakdown'] = expense_breakdown_data
            
            logger.info(f"Chat Service: Found {len(expense_breakdown_data)} expense types")
            
            # 4. Budget records for specific queries
            budget_query = BudgetExpense.objects.select_related(
                'portfolio', 'department', 'program'
            ).all()
            
            if 'department' in entities:
                dept_name = entities['department']
                budget_query = budget_query.filter(
                    Q(department__name__icontains=dept_name) |
                    Q(portfolio__name__icontains=dept_name)
                )
                
            if 'portfolio' in entities:
                portfolio_name = entities['portfolio']
                budget_query = budget_query.filter(
                    portfolio__name__icontains=portfolio_name
                )
                
            # Limit results for performance but get detailed budget records
            budget_records = list(budget_query[:100].values(
                'id', 'department__name', 'portfolio__name', 'program__name',
                'amount_2024_25', 'amount_2023_24', 'amount_2025_26', 'amount_2026_27', 'amount_2027_28',
                'expense_type', 'appropriation_type', 'description', 'created_at'
            ))
            data['budget_records'] = budget_records
            
            # 5. All portfolios with enhanced details (DASHBOARD COMPATIBLE)
            portfolios = list(Portfolio.objects.annotate(
                department_count=Count('departments'),
                total_budget_2024_25=Sum('budgetexpense__amount_2024_25')
            ).values(
                'id', 'name', 'description', 'department_count', 'total_budget_2024_25'
            ).order_by('name'))
            data['portfolios'] = portfolios
            
            logger.info(f"Chat Service: Found {len(portfolios)} portfolios total")
            for p in portfolios[:5]:
                logger.info(f"  Portfolio: {p['name']} - Budget: {p.get('total_budget_2024_25', 'N/A')}")
            
            # 6. All departments with enhanced details (DASHBOARD COMPATIBLE)
            departments = list(Department.objects.select_related('portfolio').annotate(
                program_count=Count('programs'),
                total_budget=Sum('budgetexpense__amount_2024_25')
            ).values(
                'id', 'name', 'short_name', 'department_type', 
                'portfolio__name', 'program_count', 'total_budget'
            ).order_by('portfolio__name', 'name')[:100])
            data['departments'] = departments
            
            # 7. Comprehensive summary statistics (EXACT DASHBOARD METRICS)
            total_budget_current = basic_stats['total_budget'] or 0
            total_budget_previous = BudgetExpense.objects.filter(
                amount_2023_24__isnull=False
            ).aggregate(total=Sum('amount_2023_24'))['total'] or 0
            
            data['summary_stats'] = {
                'fiscal_year': fiscal_year,
                'total_budget': float(total_budget_current),
                'total_budget_2024_25': float(total_budget_current),
                'total_budget_2023_24': float(total_budget_previous),
                'year_over_year_change': ((total_budget_current - total_budget_previous) / total_budget_previous * 100) if total_budget_previous > 0 else 0,
                'portfolio_count': basic_stats['portfolio_count'],
                'department_count': basic_stats['department_count'],
                'program_count': basic_stats['program_count'],
                'total_records': basic_stats['expense_count']
            }
            
            # 8. Dashboard-specific metrics for detailed analysis
            data['dashboard_metrics'] = {
                'top_portfolios_formatted': [
                    {
                        'name': p['name'],
                        'amount_billions': round(p['amount'] / 1000000000, 1),
                        'amount_formatted': f"${p['amount'] / 1000000000:.1f}B"
                    } for p in top_portfolios_data[:5]
                ],
                'largest_expenses': [
                    {
                        'type': e['type'],
                        'amount_billions': round(e['amount'] / 1000000000, 1),
                        'percentage_of_total': round((e['amount'] / total_budget_current * 100), 1) if total_budget_current > 0 else 0
                    } for e in expense_breakdown_data[:5]
                ],
                'budget_comparison': {
                    'current_year': fiscal_year,
                    'current_amount': float(total_budget_current),
                    'previous_amount': float(total_budget_previous),
                    'change_amount': float(total_budget_current - total_budget_previous),
                    'change_percentage': round(((total_budget_current - total_budget_previous) / total_budget_previous * 100), 2) if total_budget_previous > 0 else 0
                }
            }
            
            # 9. Trends data (for chart compatibility)
            if intent in ['dashboard_inquiry', 'comparison_query', 'ranking_query']:
                # Get multi-year data for trending
                years_data = []
                for year_suffix in ['2023_24', '2024_25', '2025_26', '2026_27', '2027_28']:
                    year_display = year_suffix.replace('_', '-')
                    year_total = BudgetExpense.objects.filter(
                        **{f'amount_{year_suffix}__isnull': False}
                    ).aggregate(total=Sum(f'amount_{year_suffix}'))['total'] or 0
                    
                    if year_total > 0:  # Only include years with data
                        years_data.append({
                            'fiscal_year': year_display,
                            'total_amount': float(year_total),
                            'amount_billions': round(year_total / 1000000000, 1)
                        })
                
                data['trends_data'] = years_data
            
            # DISABLE CACHE FOR DEBUGGING
            # cache.set(cache_key, data, self.cache_timeout)
            
        except Exception as e:
            logger.error(f"Error retrieving government data: {e}", exc_info=True)
            
        return data


class GoogleGeminiService:
    """Service for interacting with Google Gemini AI API"""
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_AI_API_KEY', '')
        self.base_url = 'https://generativelanguage.googleapis.com/v1beta'
        self.default_model = os.getenv('DEFAULT_AI_MODEL', 'gemini-1.5-flash')
        self.temperature = float(os.getenv('AI_TEMPERATURE', '0.1'))
        self.max_tokens = int(os.getenv('AI_MAX_TOKENS', '2000'))
        
        # For development/testing, allow operation without API key
        self.mock_mode = not self.api_key
        if self.mock_mode:
            logger.warning("Google AI API key not found. Running in mock mode.")
    
    def create_system_prompt(self, government_data: Dict) -> str:
        """Create system prompt with government data context - ENHANCED FOR DASHBOARD COMPATIBILITY"""
        # Convert data to JSON-serializable format
        safe_data = self._make_json_safe(government_data)
        
        # Log the actual data being passed to the AI
        logger.info(f"Chat Service: Creating system prompt with data keys: {list(safe_data.keys())}")
        logger.info(f"Chat Service: Top portfolios in prompt: {safe_data.get('top_portfolios', [])}")
        logger.info(f"Chat Service: Total portfolios in data: {len(safe_data.get('portfolios', []))}")
        
        # Extract key statistics for the prompt
        summary_stats = safe_data.get('summary_stats', {})
        top_portfolios = safe_data.get('top_portfolios', [])[:5]  # Top 5 for brevity
        expense_breakdown = safe_data.get('expense_breakdown', [])[:3]  # Top 3 expense types
        dashboard_metrics = safe_data.get('dashboard_metrics', {})
        trends_data = safe_data.get('trends_data', [])
        
        # Format dashboard-style data presentation
        portfolio_summary = "\n".join([
            f"- {p['name']}: ${p['amount']:,.0f} AUD (${p['amount']/1000000000:.1f}B)"
            for p in top_portfolios
        ])
        
        expense_summary = "\n".join([
            f"- {e['type']}: ${e['amount']:,.0f} AUD ({e['count']} items)"
            for e in expense_breakdown
        ])
        
        trends_summary = "\n".join([
            f"- {t['fiscal_year']}: ${t['total_amount']:,.0f} AUD (${t['amount_billions']}B)"
            for t in trends_data
        ]) if trends_data else "Multi-year trend data available for 2023-24 through 2027-28"
        
        return f"""You are a trustworthy AI assistant for the Australian Government Budget Analysis System. Your role is to provide accurate, reliable answers based on the EXACT SAME DATA that powers the government budget dashboard.

CRITICAL REQUIREMENTS:
1. DASHBOARD PARITY: You have access to the EXACT SAME comprehensive dataset as the dashboard
2. ACCURACY FIRST: Only provide information that can be verified from the provided government dataset
3. TRUST SCORING: Always be conservative with confidence levels
4. CITE SOURCES: Reference specific data points from the government dataset
5. NO HALLUCINATION: If data is not available, clearly state this limitation
6. AUSTRALIAN CONTEXT: All amounts are in Australian Dollars (AUD)
7. DASHBOARD ANALYSIS: Provide insights similar to what users see in the dashboard

COMPREHENSIVE GOVERNMENT DATA AVAILABLE (IDENTICAL TO DASHBOARD):

📊 BUDGET OVERVIEW (FISCAL YEAR {summary_stats.get('fiscal_year', '2024-25')}):
- Total Budget: ${summary_stats.get('total_budget', 0):,.0f} AUD
- Previous Year: ${summary_stats.get('total_budget_2023_24', 0):,.0f} AUD
- Year-over-Year Change: {summary_stats.get('year_over_year_change', 0):+.1f}%
- Total Portfolios: {summary_stats.get('portfolio_count', 0)}
- Total Departments: {summary_stats.get('department_count', 0)}
- Total Programs: {summary_stats.get('program_count', 0)}
- Data Records: {summary_stats.get('total_records', 0):,}

🏆 TOP PORTFOLIOS BY BUDGET ALLOCATION:
{portfolio_summary}

📋 EXPENSE CATEGORIES BREAKDOWN:
{expense_summary}

📈 MULTI-YEAR BUDGET TRENDS:
{trends_summary}

🎯 DASHBOARD-STYLE METRICS AVAILABLE:
- Portfolio comparisons and rankings
- Department budget breakdowns
- Program-level expense details
- Year-over-year growth analysis
- Expense type distributions
- Appropriation type analysis

DETAILED DATASET STRUCTURE:
{chr(10).join([f"- {key}: {len(value) if isinstance(value, list) else type(value).__name__}" for key, value in safe_data.items()])}

QUERY HANDLING CAPABILITIES:
✅ Dashboard-style summaries ("Show me the budget overview")
✅ Portfolio rankings ("Top spending portfolios")
✅ Department comparisons ("Compare health vs education spending")
✅ Trend analysis ("Budget changes over time")
✅ Expense breakdowns ("How is money allocated?")
✅ Specific searches ("Find Medicare programs")
✅ Financial calculations ("Total government spending")
✅ Data insights ("Largest budget increases")

RESPONSE GUIDELINES:
- Provide dashboard-quality analysis and insights
- Use specific numbers from the comprehensive dataset
- Compare current vs previous year data when relevant
- Reference portfolio and department relationships
- Format financial figures clearly (e.g., $123.45 billion AUD)
- Explain the data source and time period (primarily 2024-25 budget)
- Highlight trends, patterns, and significant findings
- Use professional, government-appropriate language
- Provide context for budget allocations and policy areas

TRUST SCORE GUIDELINES:
- High confidence (0.8-1.0): Data directly available in comprehensive dataset
- Medium confidence (0.6-0.8): Calculated from available data with clear methodology
- Low confidence (0.3-0.6): Inferred from patterns or estimated with caveats
- Very low confidence (0.0-0.3): Insufficient data available for reliable answer

You have access to the complete Australian Government Budget dataset that includes:
- All portfolio and department budget allocations
- Multi-year spending trends and comparisons
- Program-level expense details and descriptions
- Appropriation types and expense categorizations
- The same analytical capabilities as the official budget dashboard

Provide insights with the same depth and accuracy as government budget analysts."""
    
    
    def _make_json_safe(self, data):
        """Convert data to JSON-serializable format"""
        import uuid
        import decimal
        from datetime import datetime, date
        
        if isinstance(data, dict):
            return {k: self._make_json_safe(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._make_json_safe(item) for item in data]
        elif isinstance(data, uuid.UUID):
            return str(data)
        elif isinstance(data, (datetime, date)):
            return data.isoformat()
        elif isinstance(data, decimal.Decimal):
            return float(data)
        else:
            return data

    def call_gemini_api(self, messages: List[Dict], model: str = None) -> Dict:
        """Make API call to Google Gemini"""
        # If no API key, return mock response
        if self.mock_mode:
            return {
                'candidates': [{
                    'content': {
                        'parts': [{
                            'text': f"Based on the Australian government data available, I can help you with budget and department information. However, I'm currently running in demo mode. To access the full AI capabilities, please configure the Google AI API key.\n\nYour query was processed and I have access to government budget data including portfolios, departments, and spending information."
                        }]
                    }
                }],
                'model': 'mock-model'
            }
        
        # Convert OpenAI format messages to Gemini format
        gemini_contents = []
        system_instruction = None
        
        for message in messages:
            if message['role'] == 'system':
                system_instruction = message['content']
            elif message['role'] in ['user', 'assistant']:
                gemini_contents.append({
                    'role': 'user' if message['role'] == 'user' else 'model',
                    'parts': [{'text': message['content']}]
                })
        
        model_name = model or self.default_model
        url = f"{self.base_url}/models/{model_name}:generateContent?key={self.api_key}"
        
        payload = {
            'contents': gemini_contents,
            'generationConfig': {
                'temperature': self.temperature,
                'maxOutputTokens': self.max_tokens,
                'topP': 0.95
            }
        }
        
        # Add system instruction if available
        if system_instruction:
            payload['systemInstruction'] = {
                'parts': [{'text': system_instruction}]
            }
        
        try:
            response = requests.post(
                url,
                headers={'Content-Type': 'application/json'},
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Google Gemini API error: {e}")
            # Return fallback response instead of raising
            return {
                'candidates': [{
                    'content': {
                        'parts': [{
                            'text': f"I apologize, but I'm experiencing connectivity issues with the AI service. However, I can confirm that your query about Australian government data has been received. Please try again in a moment."
                        }]
                    }
                }],
                'model': 'fallback-model'
            }
    
    def calculate_trust_score(self, response_content: str, data_availability: Dict) -> float:
        """Calculate trust score based on response and data availability"""
        base_score = 0.5
        
        # Increase trust if specific numbers are mentioned
        if any(char.isdigit() for char in response_content):
            base_score += 0.2
            
        # Increase trust if data sources are available
        if data_availability.get('budget_records'):
            base_score += 0.1
            
        # Increase trust if specific departments/portfolios mentioned
        if data_availability.get('departments') or data_availability.get('portfolios'):
            base_score += 0.1
            
        # Decrease trust if response contains uncertainty indicators
        uncertainty_words = ['might', 'could', 'approximately', 'estimated', 'unclear']
        if any(word in response_content.lower() for word in uncertainty_words):
            base_score -= 0.1
            
        # Ensure trust score is within valid range
        return max(0.0, min(1.0, base_score))


class GovHackAIService:
    """Main AI service combining Google Gemini and government data"""
    
    def __init__(self):
        self.gemini = GoogleGeminiService()
        self.data_retriever = GovernmentDataRetriever()
    
    def process_query(self, user_query: str, conversation_history: List[Dict] = None) -> AIResponse:
        """Process user query and generate AI response"""
        start_time = time.time()
        
        try:
            # Extract intent and entities
            intent, entities = self.data_retriever.extract_intent_and_entities(user_query)
            
            # Retrieve relevant government data
            government_data = self.data_retriever.get_relevant_data(intent, entities)
            
            # Create system prompt with data context
            system_prompt = self.gemini.create_system_prompt(government_data)
            
            # Prepare messages for Gemini
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add conversation history if available
            if conversation_history:
                messages.extend(conversation_history[-6:])  # Last 6 messages for context
            
            # Add current user query
            messages.append({"role": "user", "content": user_query})
            
            # Call Gemini API
            ai_response = self.gemini.call_gemini_api(messages)
            
            # Extract response content from Gemini format
            if 'candidates' in ai_response and ai_response['candidates']:
                response_content = ai_response['candidates'][0]['content']['parts'][0]['text']
                model_used = ai_response.get('model', self.gemini.default_model)
            else:
                # Fallback if response format is unexpected
                response_content = "I apologize, but I received an unexpected response format from the AI service."
                model_used = 'fallback-model'
            
            # Calculate trust score
            trust_score = self.gemini.calculate_trust_score(
                response_content, government_data
            )
            
            # Determine data sources used
            data_sources = []
            if government_data['budget_records']:
                data_sources.append('budget_2024_25')
            if government_data['portfolios']:
                data_sources.append('portfolios')
            if government_data['departments']:
                data_sources.append('departments')
            
            processing_time = time.time() - start_time
            
            return AIResponse(
                content=response_content,
                trust_score=trust_score,
                processing_time=processing_time,
                data_sources=data_sources,
                intent=intent,
                entities=entities,
                model_used=model_used
            )
            
        except Exception as e:
            logger.error(f"Error processing AI query: {e}")
            
            # Return fallback response
            return AIResponse(
                content=f"I apologize, but I encountered an error processing your query about Australian government data. Please try rephrasing your question or contact support if the issue persists.",
                trust_score=0.0,
                processing_time=time.time() - start_time,
                data_sources=[],
                intent=intent if 'intent' in locals() else 'error',
                entities=entities if 'entities' in locals() else {},
                model_used="fallback"
            )


# Global service instance
ai_service = GovHackAIService()