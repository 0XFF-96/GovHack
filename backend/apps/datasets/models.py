from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid


class Portfolio(models.Model):
    """政府部门组合模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True, verbose_name='部门组合名称')
    description = models.TextField(blank=True, verbose_name='描述')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'portfolios'
        verbose_name = '部门组合'
        verbose_name_plural = '部门组合'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Department(models.Model):
    """政府部门/机构模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='departments', verbose_name='所属部门组合')
    name = models.CharField(max_length=300, verbose_name='部门/机构名称')
    short_name = models.CharField(max_length=50, blank=True, verbose_name='简称')
    department_type = models.CharField(max_length=50, default='Agency', verbose_name='部门类型')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'departments'
        verbose_name = '政府部门'
        verbose_name_plural = '政府部门'
        ordering = ['portfolio__name', 'name']
        unique_together = ['portfolio', 'name']
    
    def __str__(self):
        return f"{self.portfolio.name} - {self.name}"


class Outcome(models.Model):
    """政府目标成果模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='outcomes', verbose_name='所属部门')
    outcome_number = models.CharField(max_length=20, verbose_name='目标编号')
    description = models.TextField(verbose_name='目标描述')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'outcomes'
        verbose_name = '目标成果'
        verbose_name_plural = '目标成果'
        ordering = ['department__name', 'outcome_number']
        unique_together = ['department', 'outcome_number']
    
    def __str__(self):
        return f"{self.department.name} - {self.outcome_number}"


class Program(models.Model):
    """政府项目模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='programs', verbose_name='所属部门')
    outcome = models.ForeignKey(Outcome, on_delete=models.CASCADE, related_name='programs', verbose_name='对应目标')
    program_number = models.CharField(max_length=20, verbose_name='项目编号')
    name = models.CharField(max_length=400, verbose_name='项目名称')
    description = models.TextField(blank=True, verbose_name='项目描述')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'programs'
        verbose_name = '政府项目'
        verbose_name_plural = '政府项目'
        ordering = ['department__name', 'program_number']
        unique_together = ['department', 'program_number']
    
    def __str__(self):
        return f"{self.program_number}: {self.name}"


class BudgetExpense(models.Model):
    """预算支出明细模型"""
    EXPENSE_TYPE_CHOICES = [
        ('Departmental Expenses', '部门支出'),
        ('Administered Expenses', '管理支出'),
        ('Administered Capital', '管理资本'),
        ('Special Appropriation', '特殊拨款'),
        ('Other', '其他'),
    ]
    
    APPROPRIATION_TYPE_CHOICES = [
        ('Departmental appropriation', '部门拨款'),
        ('s74 External Revenue', 'S74外部收入'),
        ('Administered appropriation', '管理拨款'),
        ('Special appropriation', '特殊拨款'),
        ('Expenses not requiring appropriation in the Budget year', '预算年度不需要拨款的支出'),
        ('Other', '其他'),
    ]
    
    FISCAL_YEAR_CHOICES = [
        ('2023-24', '2023-24财年'),
        ('2024-25', '2024-25财年'),
        ('2025-26', '2025-26财年'),
        ('2026-27', '2026-27财年'),
        ('2027-28', '2027-28财年'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, verbose_name='部门组合')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='部门/机构')
    program = models.ForeignKey(Program, on_delete=models.CASCADE, verbose_name='项目')
    outcome = models.ForeignKey(Outcome, on_delete=models.CASCADE, verbose_name='目标成果')
    
    expense_type = models.CharField(max_length=100, choices=EXPENSE_TYPE_CHOICES, verbose_name='支出类型')
    appropriation_type = models.CharField(max_length=150, choices=APPROPRIATION_TYPE_CHOICES, verbose_name='拨款类型')
    description = models.TextField(blank=True, verbose_name='支出描述')
    
    # 各财年预算金额(单位：千澳元)
    amount_2023_24 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, 
                                        validators=[MinValueValidator(0)], verbose_name='2023-24财年金额')
    amount_2024_25 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                        validators=[MinValueValidator(0)], verbose_name='2024-25财年金额')
    amount_2025_26 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                        validators=[MinValueValidator(0)], verbose_name='2025-26财年金额')
    amount_2026_27 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                        validators=[MinValueValidator(0)], verbose_name='2026-27财年金额')
    amount_2027_28 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                        validators=[MinValueValidator(0)], verbose_name='2027-28财年金额')
    
    # 数据来源信息
    source_document = models.CharField(max_length=200, blank=True, verbose_name='源文档')
    source_table = models.CharField(max_length=100, blank=True, verbose_name='源表格')
    source_url = models.URLField(blank=True, verbose_name='源URL')
    
    # 元数据
    raw_data_hash = models.CharField(max_length=64, blank=True, verbose_name='原始数据哈希')
    import_batch = models.CharField(max_length=100, blank=True, verbose_name='导入批次')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'budget_expenses'
        verbose_name = '预算支出'
        verbose_name_plural = '预算支出'
        ordering = ['portfolio__name', 'department__name', 'program__program_number']
        indexes = [
            models.Index(fields=['portfolio', 'department']),
            models.Index(fields=['expense_type']),
            models.Index(fields=['appropriation_type']),
            models.Index(fields=['amount_2024_25']),
            models.Index(fields=['import_batch']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.portfolio.name} - {self.program.name} - {self.expense_type}"
    
    def get_amount_by_fiscal_year(self, fiscal_year: str):
        """根据财年获取金额"""
        amount_fields = {
            '2023-24': self.amount_2023_24,
            '2024-25': self.amount_2024_25,
            '2025-26': self.amount_2025_26,
            '2026-27': self.amount_2026_27,
            '2027-28': self.amount_2027_28,
        }
        return amount_fields.get(fiscal_year)
    
    def get_total_amount(self):
        """获取所有财年总金额"""
        amounts = [
            self.amount_2023_24 or 0,
            self.amount_2024_25 or 0,
            self.amount_2025_26 or 0,
            self.amount_2026_27 or 0,
            self.amount_2027_28 or 0,
        ]
        return sum(amounts)


class DataImportLog(models.Model):
    """数据导入日志模型"""
    STATUS_CHOICES = [
        ('started', '开始'),
        ('processing', '处理中'),
        ('completed', '完成'),
        ('failed', '失败'),
        ('cancelled', '取消'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch_id = models.CharField(max_length=100, unique=True, verbose_name='批次ID')
    source_file = models.CharField(max_length=500, verbose_name='源文件路径')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='started', verbose_name='状态')
    
    total_rows = models.IntegerField(default=0, verbose_name='总行数')
    processed_rows = models.IntegerField(default=0, verbose_name='已处理行数')
    success_rows = models.IntegerField(default=0, verbose_name='成功行数')
    error_rows = models.IntegerField(default=0, verbose_name='错误行数')
    
    start_time = models.DateTimeField(default=timezone.now, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    duration_seconds = models.FloatField(null=True, blank=True, verbose_name='持续时间(秒)')
    
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    import_summary = models.JSONField(default=dict, verbose_name='导入摘要')
    
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'data_import_logs'
        verbose_name = '数据导入日志'
        verbose_name_plural = '数据导入日志'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"导入批次 {self.batch_id} - {self.get_status_display()}"
    
    def calculate_success_rate(self):
        """计算成功率"""
        if self.processed_rows == 0:
            return 0
        return (self.success_rows / self.processed_rows) * 100


class FinanceRecord(models.Model):
    """财务记录模型 - 用于RAG知识库"""
    RECORD_TYPE_CHOICES = [
        ('payment', '付款记录'),
        ('invoice', '发票记录'),
        ('budget_transfer', '预算转移'),
        ('expense_claim', '费用报销'),
        ('revenue', '收入记录'),
        ('other', '其他'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    record_type = models.CharField(max_length=20, choices=RECORD_TYPE_CHOICES, verbose_name='记录类型')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='finance_records', verbose_name='所属部门')
    
    # 财务信息
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='金额')
    currency = models.CharField(max_length=3, default='AUD', verbose_name='货币')
    transaction_date = models.DateField(verbose_name='交易日期')
    reference_number = models.CharField(max_length=100, unique=True, verbose_name='参考编号')
    
    # 详细信息
    description = models.TextField(verbose_name='描述')
    supplier_name = models.CharField(max_length=200, blank=True, verbose_name='供应商名称')
    account_code = models.CharField(max_length=50, blank=True, verbose_name='账户代码')
    
    # 状态信息
    status = models.CharField(max_length=20, default='pending', verbose_name='状态')
    approval_status = models.CharField(max_length=20, default='pending', verbose_name='审批状态')
    
    # 元数据
    source_document = models.CharField(max_length=200, blank=True, verbose_name='源文档')
    created_by = models.CharField(max_length=100, blank=True, verbose_name='创建人')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'finance_records'
        verbose_name = '财务记录'
        verbose_name_plural = '财务记录'
        ordering = ['-transaction_date', '-created_at']
        indexes = [
            models.Index(fields=['record_type']),
            models.Index(fields=['department']),
            models.Index(fields=['transaction_date']),
            models.Index(fields=['supplier_name']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.record_type} - {self.reference_number} - {self.amount}"


class HRRecord(models.Model):
    """人力资源记录模型 - 用于RAG知识库"""
    RECORD_TYPE_CHOICES = [
        ('employment', '雇佣记录'),
        ('salary', '薪资记录'),
        ('leave', '请假记录'),
        ('performance', '绩效记录'),
        ('training', '培训记录'),
        ('termination', '终止记录'),
        ('other', '其他'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    record_type = models.CharField(max_length=20, choices=RECORD_TYPE_CHOICES, verbose_name='记录类型')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='hr_records', verbose_name='所属部门')
    
    # 人员信息
    employee_id = models.CharField(max_length=50, verbose_name='员工ID')
    employee_name = models.CharField(max_length=200, verbose_name='员工姓名')
    position = models.CharField(max_length=200, verbose_name='职位')
    employment_type = models.CharField(max_length=50, verbose_name='雇佣类型')
    
    # 记录详情
    description = models.TextField(verbose_name='描述')
    start_date = models.DateField(verbose_name='开始日期')
    end_date = models.DateField(null=True, blank=True, verbose_name='结束日期')
    
    # 数值信息
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='金额')
    days = models.IntegerField(null=True, blank=True, verbose_name='天数')
    
    # 状态信息
    status = models.CharField(max_length=20, default='active', verbose_name='状态')
    approval_status = models.CharField(max_length=20, default='pending', verbose_name='审批状态')
    
    # 元数据
    source_document = models.CharField(max_length=200, blank=True, verbose_name='源文档')
    created_by = models.CharField(max_length=100, blank=True, verbose_name='创建人')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'hr_records'
        verbose_name = '人力资源记录'
        verbose_name_plural = '人力资源记录'
        ordering = ['-start_date', '-created_at']
        indexes = [
            models.Index(fields=['record_type']),
            models.Index(fields=['department']),
            models.Index(fields=['employee_id']),
            models.Index(fields=['employee_name']),
            models.Index(fields=['start_date']),
        ]
    
    def __str__(self):
        return f"{self.record_type} - {self.employee_name} - {self.position}"


class ProcurementRecord(models.Model):
    """采购记录模型 - 用于RAG知识库"""
    RECORD_TYPE_CHOICES = [
        ('purchase_order', '采购订单'),
        ('contract', '合同记录'),
        ('tender', '招标记录'),
        ('supplier_evaluation', '供应商评估'),
        ('delivery', '交付记录'),
        ('payment', '付款记录'),
        ('other', '其他'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    record_type = models.CharField(max_length=20, choices=RECORD_TYPE_CHOICES, verbose_name='记录类型')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='procurement_records', verbose_name='所属部门')
    
    # 采购信息
    contract_number = models.CharField(max_length=100, unique=True, verbose_name='合同编号')
    supplier_name = models.CharField(max_length=200, verbose_name='供应商名称')
    supplier_abn = models.CharField(max_length=20, blank=True, verbose_name='供应商ABN')
    
    # 合同详情
    description = models.TextField(verbose_name='描述')
    contract_value = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='合同价值')
    start_date = models.DateField(verbose_name='开始日期')
    end_date = models.DateField(verbose_name='结束日期')
    
    # 分类信息
    category = models.CharField(max_length=100, verbose_name='采购类别')
    subcategory = models.CharField(max_length=100, blank=True, verbose_name='子类别')
    
    # 状态信息
    status = models.CharField(max_length=20, default='active', verbose_name='状态')
    approval_status = models.CharField(max_length=20, default='pending', verbose_name='审批状态')
    
    # 元数据
    source_document = models.CharField(max_length=200, blank=True, verbose_name='源文档')
    created_by = models.CharField(max_length=100, blank=True, verbose_name='创建人')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'procurement_records'
        verbose_name = '采购记录'
        verbose_name_plural = '采购记录'
        ordering = ['-start_date', '-created_at']
        indexes = [
            models.Index(fields=['record_type']),
            models.Index(fields=['department']),
            models.Index(fields=['supplier_name']),
            models.Index(fields=['contract_number']),
            models.Index(fields=['start_date']),
        ]
    
    def __str__(self):
        return f"{self.record_type} - {self.contract_number} - {self.supplier_name}"


class DocumentVector(models.Model):
    """文档向量模型 - 用于RAG检索"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # 关联记录
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE, verbose_name='内容类型')
    object_id = models.UUIDField(verbose_name='对象ID')
    
    # 向量信息
    content_hash = models.CharField(max_length=64, verbose_name='内容哈希')
    content_text = models.TextField(verbose_name='内容文本')
    vector_embedding = models.JSONField(verbose_name='向量嵌入')
    
    # 元数据
    source_table = models.CharField(max_length=100, verbose_name='源表')
    record_id = models.UUIDField(verbose_name='记录ID')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    
    class Meta:
        db_table = 'document_vectors'
        verbose_name = '文档向量'
        verbose_name_plural = '文档向量'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['source_table', 'record_id']),
            models.Index(fields=['content_hash']),
        ]
    
    def __str__(self):
        return f"Vector for {self.source_table}:{self.record_id}"