from rest_framework import serializers
from .models import Portfolio, Department, Outcome, Program, BudgetExpense, DataImportLog


class PortfolioSerializer(serializers.ModelSerializer):
    department_count = serializers.SerializerMethodField()
    total_budget = serializers.SerializerMethodField()
    
    class Meta:
        model = Portfolio
        fields = ['id', 'name', 'description', 'department_count', 'total_budget', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_department_count(self, obj):
        return obj.departments.count()
    
    def get_total_budget(self, obj):
        # 计算2024-25财年总预算
        total = 0
        for dept in obj.departments.all():
            for expense in dept.budgetexpense_set.all():
                if expense.amount_2024_25:
                    total += expense.amount_2024_25
        return float(total)


class DepartmentSerializer(serializers.ModelSerializer):
    portfolio_name = serializers.CharField(source='portfolio.name', read_only=True)
    program_count = serializers.SerializerMethodField()
    total_budget = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = [
            'id', 'name', 'short_name', 'department_type', 
            'portfolio_name', 'program_count', 'total_budget', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_program_count(self, obj):
        return obj.programs.count()
    
    def get_total_budget(self, obj):
        # 计算2024-25财年总预算
        total = 0
        for expense in obj.budgetexpense_set.all():
            if expense.amount_2024_25:
                total += expense.amount_2024_25
        return float(total)


class OutcomeSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = Outcome
        fields = ['id', 'outcome_number', 'description', 'department_name']


class ProgramSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    outcome_number = serializers.CharField(source='outcome.outcome_number', read_only=True)
    
    class Meta:
        model = Program
        fields = [
            'id', 'program_number', 'name', 'description',
            'department_name', 'outcome_number'
        ]


class BudgetExpenseSerializer(serializers.ModelSerializer):
    portfolio_name = serializers.CharField(source='portfolio.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    program_name = serializers.CharField(source='program.name', read_only=True)
    program_number = serializers.CharField(source='program.program_number', read_only=True)
    total_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = BudgetExpense
        fields = [
            'id', 'portfolio_name', 'department_name', 'program_name', 'program_number',
            'expense_type', 'appropriation_type', 'description',
            'amount_2023_24', 'amount_2024_25', 'amount_2025_26', 'amount_2026_27', 'amount_2027_28',
            'total_amount', 'source_document', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_total_amount(self, obj):
        return float(obj.get_total_amount())


class BudgetSearchSerializer(serializers.Serializer):
    """预算搜索请求序列化器"""
    query = serializers.CharField(max_length=500, required=False, help_text="搜索关键词")
    portfolio = serializers.CharField(max_length=200, required=False, help_text="部门组合名称")
    department = serializers.CharField(max_length=300, required=False, help_text="部门名称")
    expense_type = serializers.CharField(max_length=100, required=False, help_text="支出类型")
    fiscal_year = serializers.ChoiceField(
        choices=['2023-24', '2024-25', '2025-26', '2026-27', '2027-28'],
        required=False,
        help_text="财政年度"
    )
    min_amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, help_text="最小金额")
    max_amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, help_text="最大金额")
    limit = serializers.IntegerField(min_value=1, max_value=1000, default=50, help_text="结果数量限制")
    offset = serializers.IntegerField(min_value=0, default=0, help_text="偏移量")


class BudgetSearchResponseSerializer(serializers.Serializer):
    """预算搜索响应序列化器"""
    results = BudgetExpenseSerializer(many=True, help_text="搜索结果")
    total = serializers.IntegerField(help_text="总结果数")
    query_time = serializers.FloatField(help_text="查询耗时(秒)")
    aggregations = serializers.JSONField(help_text="聚合统计")


class BudgetSummarySerializer(serializers.Serializer):
    """预算摘要序列化器"""
    fiscal_year = serializers.CharField(help_text="财政年度")
    total_budget = serializers.DecimalField(max_digits=20, decimal_places=2, help_text="总预算")
    portfolio_count = serializers.IntegerField(help_text="部门组合数量")
    department_count = serializers.IntegerField(help_text="部门数量")
    program_count = serializers.IntegerField(help_text="项目数量")
    top_portfolios = serializers.JSONField(help_text="预算最高的部门组合")
    expense_breakdown = serializers.JSONField(help_text="支出类型分解")


class BudgetTrendSerializer(serializers.Serializer):
    """预算趋势序列化器"""
    entity_type = serializers.ChoiceField(choices=['portfolio', 'department'], help_text="实体类型")
    entity_name = serializers.CharField(help_text="实体名称")
    trend_data = serializers.JSONField(help_text="趋势数据")


class DataImportLogSerializer(serializers.ModelSerializer):
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = DataImportLog
        fields = [
            'id', 'batch_id', 'source_file', 'status',
            'total_rows', 'processed_rows', 'success_rows', 'error_rows',
            'success_rate', 'start_time', 'end_time', 'duration_seconds',
            'import_summary'
        ]
    
    def get_success_rate(self, obj):
        return obj.calculate_success_rate()