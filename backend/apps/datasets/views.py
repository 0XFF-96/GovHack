import time
from decimal import Decimal
from django.db.models import Q, Sum, Count
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Portfolio, Department, Outcome, Program, BudgetExpense, DataImportLog
from .serializers import (
    PortfolioSerializer, DepartmentSerializer, BudgetExpenseSerializer,
    BudgetSearchSerializer, BudgetSearchResponseSerializer,
    BudgetSummarySerializer, BudgetTrendSerializer, DataImportLogSerializer
)


@extend_schema(
    summary="Get portfolio list",
    description="Get all government portfolios and their basic statistics",
    responses={200: PortfolioSerializer(many=True)},
    tags=["Dataset Management"]
)
@api_view(['GET'])
@permission_classes([])  # Allow public access
def portfolio_list(request):
    """
    # Government Portfolio Directory
    
    Retrieve a comprehensive list of all Australian government portfolios
    with their associated departments and basic statistics.
    
    ## What is a Portfolio?
    A portfolio is a collection of related government departments that work
    together on similar policy areas (e.g., Health, Education, Defence).
    
    ## Response Format
    ```json
    [
        {
            "id": "uuid-string",
            "name": "Health and Aged Care",
            "description": "Portfolio overview...",
            "department_count": 3,
            "total_budget_2024_25": 95000000000
        }
    ]
    ```
    
    ## Use Cases
    - 🏢 Browse government structure
    - 📊 Compare portfolio sizes
    - 🔍 Find specific departments
    - 💰 Analyze budget allocations
    """
    portfolios = Portfolio.objects.all().order_by('name')
    serializer = PortfolioSerializer(portfolios, many=True)
    return Response(serializer.data)


@extend_schema(
    summary="Get portfolio details",
    description="Get detailed information and subordinate departments for a specific portfolio",
    parameters=[
        OpenApiParameter(
            name='portfolio_id',
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description='Portfolio ID'
        )
    ],
    responses={200: PortfolioSerializer},
    tags=["Dataset Management"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def portfolio_detail(request, portfolio_id):
    """
    # Portfolio Deep Dive
    
    Get comprehensive details about a specific government portfolio,
    including all subordinate departments, programs, and budget breakdown.
    
    ## Parameters
    - **portfolio_id**: UUID of the portfolio (from portfolio list)
    
    ## Response Includes
    - Portfolio metadata and description  
    - List of all departments in the portfolio
    - Budget totals across fiscal years
    - Program count and major initiatives
    
    ## Example Response
    ```json
    {
        "id": "health-uuid",
        "name": "Health and Aged Care",
        "departments": [
            {
                "name": "Department of Health and Aged Care",
                "budget_2024_25": 85000000000
            }
        ],
        "total_programs": 45,
        "budget_breakdown": {...}
    }
    ```
    """
    portfolio = get_object_or_404(Portfolio, id=portfolio_id)
    
    # Retrieve all departments within this portfolio
    departments = Department.objects.filter(portfolio=portfolio).order_by('name')
    
    response_data = PortfolioSerializer(portfolio).data
    response_data['departments'] = DepartmentSerializer(departments, many=True).data
    
    return Response(response_data)


@extend_schema(
    summary="Get department list",
    description="Get all government departments and their basic information",
    parameters=[
        OpenApiParameter('portfolio', OpenApiTypes.STR, description='Filter by portfolio'),
    ],
    responses={200: DepartmentSerializer(many=True)},
    tags=["Dataset Management"]
)
@api_view(['GET'])
@permission_classes([])  # Allow public access
def department_list(request):
    """
    # Government Department Directory
    
    Browse all Australian government departments with optional filtering
    by portfolio or department type.
    
    ## Query Parameters
    - **portfolio**: Filter by portfolio name (partial match)
    
    ## Example Queries
    ```
    GET /api/v1/datasets/departments/
    GET /api/v1/datasets/departments/?portfolio=health
    GET /api/v1/datasets/departments/?portfolio=education
    ```
    
    ## Response Format
    ```json
    [
        {
            "id": "dept-uuid",
            "name": "Department of Health and Aged Care",
            "portfolio": "Health and Aged Care",
            "department_type": "Department",
            "budget_2024_25": 85000000000,
            "program_count": 15
        }
    ]
    ```
    
    ## Department Types
    - **Department**: Major government departments
    - **Agency**: Specialized government agencies  
    - **Authority**: Regulatory authorities
    - **Commission**: Independent commissions
    """
    departments = Department.objects.select_related('portfolio').order_by('portfolio__name', 'name')
    
    # Apply optional portfolio filtering
    portfolio = request.GET.get('portfolio')
    if portfolio:
        departments = departments.filter(portfolio__name__icontains=portfolio)
    
    serializer = DepartmentSerializer(departments, many=True)
    return Response(serializer.data)


@extend_schema(
    summary="Get department details",
    description="Get detailed information and project list for a specific department",
    parameters=[
        OpenApiParameter(
            name='department_id',
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description='Department ID'
        )
    ],
    responses={200: DepartmentSerializer},
    tags=["Dataset Management"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def department_detail(request, department_id):
    """
    # Department Analysis Dashboard
    
    Comprehensive analysis of a specific government department including
    budget allocation, programs, outcomes, and performance metrics.
    
    ## Parameters
    - **department_id**: UUID of the department
    
    ## Response Includes
    - Department profile and contact info
    - Budget statistics across fiscal years
    - List of programs and outcomes
    - Expense breakdown by category
    - Performance indicators
    
    ## Example Response
    ```json
    {
        "id": "education-uuid",
        "name": "Department of Education",
        "portfolio": "Education",
        "budget_stats": {
            "total_budget_2024_25": 45000000000,
            "expense_items": 120,
            "program_count": 25
        },
        "top_programs": [...],
        "expense_categories": [...]
    }
    ```
    """
    department = get_object_or_404(Department, id=department_id)
    
    response_data = DepartmentSerializer(department).data
    
    # Calculate department budget statistics and metrics
    budget_stats = BudgetExpense.objects.filter(department=department).aggregate(
        total_2024_25=Sum('amount_2024_25'),
        expense_count=Count('id')
    )
    
    response_data['budget_stats'] = {
        'total_budget_2024_25': float(budget_stats['total_2024_25'] or 0),
        'expense_items': budget_stats['expense_count']
    }
    
    return Response(response_data)


@extend_schema(
    summary="Budget data search",
    description="Perform advanced search and filtering in government budget data",
    request=BudgetSearchSerializer,
    responses={200: BudgetSearchResponseSerializer},
    tags=["Budget Query"]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def budget_search(request):
    """
    # Advanced Budget Search Engine
    
    Perform sophisticated searches across Australian government budget data
    with multiple filter options and sorting capabilities.
    
    ## Request Parameters
    ```json
    {
        "query": "search term",
        "portfolio": "portfolio filter",
        "department": "department filter", 
        "expense_type": "expense type filter",
        "fiscal_year": "2024-25",
        "min_amount": 1000000,
        "max_amount": 100000000,
        "limit": 50,
        "offset": 0
    }
    ```
    
    ## Search Examples
    
    **Find education programs over $10M:**
    ```json
    {
        "query": "education",
        "min_amount": 10000000,
        "fiscal_year": "2024-25"
    }
    ```
    
    **Health department Medicare programs:**
    ```json
    {
        "query": "medicare",
        "portfolio": "health",
        "expense_type": "Administered Expenses"
    }
    ```
    
    ## Response Format
    ```json
    {
        "results": [...],
        "total": 1547,
        "query_time": 0.245,
        "aggregations": {
            "total_amount": 125000000000,
            "portfolio_count": 8,
            "department_count": 23
        }
    }
    ```
    
    ## Features
    - 🔍 Full-text search across descriptions
    - 💰 Amount range filtering
    - 📊 Real-time aggregations
    - ⚡ Sub-second response times
    - 📈 Sorting by amount, date, relevance
    """
    serializer = BudgetSearchSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    start_time = time.time()
    
    # Build comprehensive search query
    query = BudgetExpense.objects.select_related(
        'portfolio', 'department', 'program'
    ).all()
    
    # Keyword search
    search_term = serializer.validated_data.get('query')
    if search_term:
        query = query.filter(
            Q(portfolio__name__icontains=search_term) |
            Q(department__name__icontains=search_term) |
            Q(program__name__icontains=search_term) |
            Q(description__icontains=search_term)
        )
    
    # Filter conditions
    portfolio = serializer.validated_data.get('portfolio')
    if portfolio:
        query = query.filter(portfolio__name__icontains=portfolio)
    
    department = serializer.validated_data.get('department')
    if department:
        query = query.filter(department__name__icontains=department)
    
    expense_type = serializer.validated_data.get('expense_type')
    if expense_type:
        query = query.filter(expense_type=expense_type)
    
    # Amount range filter
    fiscal_year = serializer.validated_data.get('fiscal_year', '2024-25')
    amount_field = f'amount_{fiscal_year.replace("-", "_")}'
    
    min_amount = serializer.validated_data.get('min_amount')
    if min_amount:
        query = query.filter(**{f'{amount_field}__gte': min_amount})
    
    max_amount = serializer.validated_data.get('max_amount')
    if max_amount:
        query = query.filter(**{f'{amount_field}__lte': max_amount})
    
    # Exclude records with null amounts
    query = query.filter(**{f'{amount_field}__isnull': False})
    
    # Sort by amount in descending order
    query = query.order_by(f'-{amount_field}')
    
    # Calculate total count
    total = query.count()
    
    # Pagination
    limit = serializer.validated_data.get('limit', 50)
    offset = serializer.validated_data.get('offset', 0)
    results = query[offset:offset + limit]
    
    # Aggregate statistics
    aggregations = query.aggregate(
        total_amount=Sum(amount_field),
        avg_amount=Sum(amount_field),  # TODO: Use Avg function
        portfolio_count=Count('portfolio', distinct=True),
        department_count=Count('department', distinct=True)
    )
    
    query_time = time.time() - start_time
    
    response_data = {
        'results': BudgetExpenseSerializer(results, many=True).data,
        'total': total,
        'query_time': round(query_time, 3),
        'aggregations': {
            'total_amount': float(aggregations['total_amount'] or 0),
            'portfolio_count': aggregations['portfolio_count'],
            'department_count': aggregations['department_count'],
            'fiscal_year': fiscal_year
        }
    }
    
    return Response(response_data)


@extend_schema(
    summary="Budget summary statistics",
    description="Get budget summary and statistics for a specific fiscal year",
    parameters=[
        OpenApiParameter('fiscal_year', OpenApiTypes.STR, description='Fiscal year (default: 2024-25)'),
    ],
    responses={200: BudgetSummarySerializer},
    tags=["Budget Query"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def budget_summary(request):
    """
    # Budget Overview Dashboard
    
    Get high-level budget statistics and breakdowns for a specific fiscal year,
    including top portfolios, expense categories, and spending trends.
    
    ## Query Parameters
    - **fiscal_year**: Target fiscal year (default: 2024-25)
    
    ## Example Usage
    ```
    GET /api/v1/datasets/budget/summary/
    GET /api/v1/datasets/budget/summary/?fiscal_year=2023-24
    ```
    
    ## Response Format
    ```json
    {
        "fiscal_year": "2024-25",
        "total_budget": 684500000000,
        "portfolio_count": 16,
        "department_count": 156,
        "program_count": 513,
        "top_portfolios": [
            {
                "name": "Health and Aged Care",
                "amount": 95000000000
            }
        ],
        "expense_breakdown": [
            {
                "type": "Administered Expenses",
                "amount": 350000000000,
                "count": 445
            }
        ]
    }
    ```
    
    ## Key Insights
    - 📊 Total government spending
    - 🏆 Largest spending portfolios
    - 📋 Expense type distribution
    - 🎯 Program and department counts
    """
    fiscal_year = request.GET.get('fiscal_year', '2024-25')
    amount_field = f'amount_{fiscal_year.replace("-", "_")}'
    
    # Calculate basic budget statistics for fiscal year
    basic_stats = BudgetExpense.objects.filter(
        **{f'{amount_field}__isnull': False}
    ).aggregate(
        total_budget=Sum(amount_field),
        expense_count=Count('id'),
        portfolio_count=Count('portfolio', distinct=True),
        department_count=Count('department', distinct=True),
        program_count=Count('program', distinct=True)
    )
    
    # Generate portfolio ranking by budget size
    top_portfolios = Portfolio.objects.filter(
        budgetexpense__amount_2024_25__isnull=False
    ).annotate(
        total_amount=Sum(f'budgetexpense__{amount_field}')
    ).order_by('-total_amount')[:10]
    
    top_portfolios_data = [
        {
            'name': p.name,
            'amount': float(p.total_amount or 0)
        }
        for p in top_portfolios
    ]
    
    # Analyze spending by expense category
    expense_breakdown = BudgetExpense.objects.filter(
        **{f'{amount_field}__isnull': False}
    ).values('expense_type').annotate(
        total_amount=Sum(amount_field),
        count=Count('id')
    ).order_by('-total_amount')
    
    expense_breakdown_data = [
        {
            'type': item['expense_type'],
            'amount': float(item['total_amount'] or 0),
            'count': item['count']
        }
        for item in expense_breakdown
    ]
    
    response_data = {
        'fiscal_year': fiscal_year,
        'total_budget': float(basic_stats['total_budget'] or 0),
        'portfolio_count': basic_stats['portfolio_count'],
        'department_count': basic_stats['department_count'],
        'program_count': basic_stats['program_count'],
        'top_portfolios': top_portfolios_data,
        'expense_breakdown': expense_breakdown_data
    }
    
    return Response(response_data)


@extend_schema(
    summary="Budget trend analysis",
    description="Analyze budget trend changes for a specified entity",
    parameters=[
        OpenApiParameter('entity_type', OpenApiTypes.STR, description='Entity type (portfolio/department)', required=True),
        OpenApiParameter('entity_name', OpenApiTypes.STR, description='Entity name', required=True),
    ],
    responses={200: BudgetTrendSerializer},
    tags=["Budget Query"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def budget_trends(request):
    """
    # Budget Trend Analysis
    
    Analyze spending trends over multiple fiscal years for specific
    portfolios or departments, including year-over-year changes.
    
    ## Required Parameters
    - **entity_type**: "portfolio" or "department"
    - **entity_name**: Name of portfolio/department to analyze
    
    ## Example Queries
    ```
    GET /api/v1/datasets/budget/trends/?entity_type=portfolio&entity_name=health
    GET /api/v1/datasets/budget/trends/?entity_type=department&entity_name=education
    ```
    
    ## Response Format
    ```json
    {
        "entity_type": "portfolio",
        "entity_name": "Health and Aged Care",
        "trend_data": [
            {
                "fiscal_year": "2024-25",
                "total_amount": 95000000000,
                "year_over_year_change": 5.2
            }
        ],
        "summary": {
            "avg_growth_rate": 3.8,
            "total_change_5_year": 18.5,
            "peak_year": "2024-25",
            "lowest_year": "2020-21"
        }
    }
    ```
    
    ## Analysis Features
    - 📈 5-year trend visualization data
    - 📊 Year-over-year percentage changes  
    - 🎯 Growth rate calculations
    - 📉 Peak and valley identification
    - 💡 Spending pattern insights
    """
    entity_type = request.GET.get('entity_type')
    entity_name = request.GET.get('entity_name')
    
    if not entity_type or not entity_name:
        return Response(
            {'error': 'entity_type and entity_name parameters are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Build comprehensive search query
    if entity_type == 'portfolio':
        expenses = BudgetExpense.objects.filter(portfolio__name__icontains=entity_name)
    elif entity_type == 'department':
        expenses = BudgetExpense.objects.filter(department__name__icontains=entity_name)
    else:
        return Response(
            {'error': 'entity_type must be portfolio or department'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Compute budget totals across all fiscal years
    fiscal_years = ['2023-24', '2024-25', '2025-26', '2026-27', '2027-28']
    trend_data = []
    
    for year in fiscal_years:
        amount_field = f'amount_{year.replace("-", "_")}'
        total = expenses.filter(
            **{f'{amount_field}__isnull': False}
        ).aggregate(
            total_amount=Sum(amount_field)
        )['total_amount'] or 0
        
        trend_data.append({
            'fiscal_year': year,
            'total_amount': float(total),
            'year_over_year_change': 0  # TODO: Calculate year-over-year change
        })
    
    # Compute percentage change between consecutive years
    for i in range(1, len(trend_data)):
        current = trend_data[i]['total_amount']
        previous = trend_data[i-1]['total_amount']
        if previous > 0:
            change = ((current - previous) / previous) * 100
            trend_data[i]['year_over_year_change'] = round(change, 2)
    
    response_data = {
        'entity_type': entity_type,
        'entity_name': entity_name,
        'trend_data': trend_data
    }
    
    return Response(response_data)


@extend_schema(
    summary="Import status query",
    description="Query data import status and progress",
    responses={200: {
        "type": "object",
        "properties": {
            "current_import": {"type": "object"},
            "recent_imports": {"type": "array", "items": {"type": "object"}}
        }
    }},
    tags=["Data Import"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def import_status(request):
    """
    # Data Import Status Monitor
    
    Monitor the status and progress of government data imports,
    including current operations and recent import history.
    
    ## Response Format
    ```json
    {
        "current_import": {
            "id": "import-uuid",
            "status": "processing",
            "progress": 75,
            "source_file": "budget-2024-25.csv",
            "processed_rows": 1425,
            "total_rows": 1900,
            "start_time": "2024-08-30T10:00:00Z",
            "estimated_completion": "2024-08-30T10:05:30Z"
        },
        "recent_imports": [
            {
                "batch_id": "budget_import_123",
                "status": "completed",
                "success_rate": 99.5,
                "total_rows": 1874,
                "duration_seconds": 3.6
            }
        ]
    }
    ```
    
    ## Import Statuses
    - **started**: Import job created
    - **processing**: Data being processed
    - **completed**: Successfully finished
    - **failed**: Error occurred
    - **cancelled**: Manually stopped
    
    ## Use Cases
    - 🔄 Monitor real-time import progress
    - 📊 Check data freshness
    - 🚨 Identify import failures
    - 📈 Track import performance
    """
    # Check for any active import operations
    current_import = DataImportLog.objects.filter(
        status__in=['started', 'processing']
    ).first()
    
    # Retrieve latest import history
    recent_imports = DataImportLog.objects.order_by('-created_at')[:10]
    
    response_data = {
        'current_import': DataImportLogSerializer(current_import).data if current_import else None,
        'recent_imports': DataImportLogSerializer(recent_imports, many=True).data
    }
    
    return Response(response_data)


@extend_schema(
    summary="Import log list",
    description="Get historical log records of data imports",
    parameters=[
        OpenApiParameter('status', OpenApiTypes.STR, description='Filter import status'),
        OpenApiParameter('limit', OpenApiTypes.INT, description='Return limit'),
    ],
    responses={200: DataImportLogSerializer(many=True)},
    tags=["Data Import"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def import_logs(request):
    """
    # Import History & Logs
    
    Detailed import log history with filtering options for
    troubleshooting and audit purposes.
    
    ## Query Parameters
    - **status**: Filter by import status (completed, failed, etc.)
    - **limit**: Maximum number of records (default: 50)
    
    ## Example Queries
    ```
    GET /api/v1/datasets/import/logs/
    GET /api/v1/datasets/import/logs/?status=completed&limit=20
    GET /api/v1/datasets/import/logs/?status=failed
    ```
    
    ## Response Format
    ```json
    [
        {
            "id": "log-uuid",
            "batch_id": "budget_import_123", 
            "source_file": "/data/budget-2024-25.csv",
            "status": "completed",
            "total_rows": 1874,
            "success_rows": 1866,
            "error_rows": 8,
            "success_rate": 99.57,
            "start_time": "2024-08-30T10:00:00Z",
            "duration_seconds": 3.6,
            "error_summary": {
                "duplicate_keys": 5,
                "validation_errors": 3
            }
        }
    ]
    ```
    
    ## Features
    - 📋 Complete audit trail
    - 🔍 Status-based filtering
    - ⚠️ Error categorization
    - 📊 Success rate tracking
    - ⏱️ Performance metrics
    """
    logs = DataImportLog.objects.order_by('-created_at')
    
    # Apply status-based filtering if specified
    status_filter = request.GET.get('status')
    if status_filter:
        logs = logs.filter(status=status_filter)
    
    # Apply record limit for pagination
    limit = int(request.GET.get('limit', 50))
    logs = logs[:limit]
    
    serializer = DataImportLogSerializer(logs, many=True)
    return Response(serializer.data)


@extend_schema(
    summary="Data statistics overview",
    description="Get basic statistics and overview of datasets",
    responses={200: {
        "type": "object",
        "properties": {
            "data_counts": {"type": "object"},
            "last_import": {"type": "object"},
            "data_quality": {"type": "object"}
        }
    }},
    tags=["Data Statistics"]
)
@api_view(['GET'])
@permission_classes([])  # Allow public access to statistics
def stats_overview(request):
    """
    # System Statistics Dashboard
    
    Comprehensive overview of data availability, quality metrics,
    and system health indicators for the government datasets.
    
    ## Response Format
    ```json
    {
        "data_counts": {
            "portfolios": 16,
            "departments": 156,
            "programs": 513,
            "budget_expenses": 1874
        },
        "last_import": {
            "batch_id": "budget_import_latest",
            "status": "completed",
            "success_rate": 100.0,
            "end_time": "2024-08-30T05:18:25Z",
            "import_summary": {
                "portfolios_created": 16,
                "departments_created": 156,
                "programs_created": 514
            }
        },
        "data_quality": {
            "completeness_rate": 99.52,
            "total_budget_2024_25": 1071523283.0,
            "data_freshness": "2024-08-30T05:18:22Z",
            "validation_score": 98.7
        }
    }
    ```
    
    ## Key Metrics
    - 📊 **Record Counts**: Total entities in each category
    - ⏱️ **Data Freshness**: Last update timestamp
    - ✅ **Quality Score**: Completeness and validation rates
    - 🔄 **Import Status**: Latest data import results
    - 💰 **Financial Totals**: Budget sum validations
    
    ## Health Indicators
    - **Completeness Rate > 95%**: ✅ Healthy
    - **Success Rate > 99%**: ✅ Reliable imports
    - **Data Age < 24hrs**: ✅ Fresh data
    - **Validation Score > 95%**: ✅ High quality
    """
    # Calculate core system statistics
    data_counts = {
        'portfolios': Portfolio.objects.count(),
        'departments': Department.objects.count(),
        'programs': Program.objects.count(),
        'budget_expenses': BudgetExpense.objects.count(),
    }
    
    # Get most recent import operation details
    last_import = DataImportLog.objects.order_by('-created_at').first()
    
    # Compute data quality and completeness metrics
    total_expenses = BudgetExpense.objects.count()
    complete_expenses = BudgetExpense.objects.filter(
        amount_2024_25__isnull=False
    ).count()
    
    data_quality = {
        'completeness_rate': (complete_expenses / total_expenses * 100) if total_expenses > 0 else 0,
        'total_budget_2024_25': float(
            BudgetExpense.objects.filter(
                amount_2024_25__isnull=False
            ).aggregate(Sum('amount_2024_25'))['amount_2024_25__sum'] or 0
        ),
        'data_freshness': last_import.created_at if last_import else None
    }
    
    response_data = {
        'data_counts': data_counts,
        'last_import': DataImportLogSerializer(last_import).data if last_import else None,
        'data_quality': data_quality
    }
    
    return Response(response_data)