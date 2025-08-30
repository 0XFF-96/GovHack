"""
Django管理命令：填充示例数据
用于测试RAG知识库功能
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import random
from decimal import Decimal

from apps.datasets.models import (
    Portfolio, Department, FinanceRecord, HRRecord, ProcurementRecord
)


class Command(BaseCommand):
    help = '填充示例数据用于测试RAG知识库功能'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制重新创建所有数据',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='每个表创建的记录数量',
        )

    def handle(self, *args, **options):
        force = options['force']
        count = options['count']

        self.stdout.write(
            self.style.SUCCESS(f'开始填充示例数据，每个表 {count} 条记录...')
        )

        try:
            # 1. 确保有基础数据
            self._ensure_base_data()
            
            # 2. 填充财务记录
            self._populate_finance_records(count, force)
            
            # 3. 填充人力资源记录
            self._populate_hr_records(count, force)
            
            # 4. 填充采购记录
            self._populate_procurement_records(count, force)
            
            self.stdout.write(
                self.style.SUCCESS('✅ 示例数据填充完成！')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 数据填充失败: {str(e)}')
            )

    def _ensure_base_data(self):
        """确保基础数据存在"""
        # 创建部门组合
        portfolios_data = [
            'Health and Aged Care',
            'Education',
            'Defence',
            'Treasury',
            'Transport and Infrastructure',
            'Agriculture, Water and the Environment',
            'Social Services',
            'Industry, Science, Energy and Resources'
        ]
        
        for name in portfolios_data:
            Portfolio.objects.get_or_create(name=name)
        
        # 为每个部门组合创建子部门
        departments_data = {
            'Health and Aged Care': ['Department of Health', 'Department of Aged Care', 'Medicare'],
            'Education': ['Department of Education', 'Department of Skills and Training', 'Australian Research Council'],
            'Defence': ['Department of Defence', 'Defence Force', 'Defence Science and Technology'],
            'Treasury': ['Department of Treasury', 'Australian Taxation Office', 'Reserve Bank'],
            'Transport and Infrastructure': ['Department of Infrastructure', 'Department of Transport', 'Infrastructure Australia'],
            'Agriculture, Water and the Environment': ['Department of Agriculture', 'Department of Environment', 'Bureau of Meteorology'],
            'Social Services': ['Department of Social Services', 'Centrelink', 'National Disability Insurance Agency'],
            'Industry, Science, Energy and Resources': ['Department of Industry', 'CSIRO', 'Australian Nuclear Science']
        }
        
        for portfolio_name, dept_names in departments_data.items():
            portfolio = Portfolio.objects.get(name=portfolio_name)
            for dept_name in dept_names:
                Department.objects.get_or_create(
                    name=dept_name,
                    portfolio=portfolio,
                    defaults={'department_type': 'Agency'}
                )

    def _populate_finance_records(self, count: int, force: bool):
        """填充财务记录"""
        if force:
            FinanceRecord.objects.all().delete()
            self.stdout.write('🗑️  清空现有财务记录')
        
        record_types = ['payment', 'invoice', 'budget_transfer', 'expense_claim', 'revenue']
        statuses = ['pending', 'approved', 'completed', 'rejected']
        approval_statuses = ['pending', 'approved', 'rejected']
        
        departments = list(Department.objects.all())
        
        for i in range(count):
            department = random.choice(departments)
            record_type = random.choice(record_types)
            amount = Decimal(random.uniform(1000, 1000000)).quantize(Decimal('0.01'))
            
            # 生成参考编号
            ref_number = f"FIN-{record_type.upper()}-{timezone.now().strftime('%Y%m')}-{i+1:04d}"
            
            # 生成交易日期（过去一年内）
            days_ago = random.randint(0, 365)
            transaction_date = date.today() - timedelta(days=days_ago)
            
            FinanceRecord.objects.create(
                record_type=record_type,
                department=department,
                amount=amount,
                currency='AUD',
                transaction_date=transaction_date,
                reference_number=ref_number,
                description=f"Sample {record_type} record for {department.name}",
                supplier_name=f"Supplier {i+1} Pty Ltd" if record_type in ['payment', 'invoice'] else None,
                account_code=f"ACC-{random.randint(1000, 9999)}" if random.random() > 0.5 else "",
                status=random.choice(statuses),
                approval_status=random.choice(approval_statuses),
                source_document=f"sample_document_{i+1}.pdf",
                created_by=f"user_{random.randint(1, 10)}"
            )
        
        self.stdout.write(f'💰 创建了 {count} 条财务记录')

    def _populate_hr_records(self, count: int, force: bool):
        """填充人力资源记录"""
        if force:
            HRRecord.objects.all().delete()
            self.stdout.write('🗑️  清空现有人力资源记录')
        
        record_types = ['employment', 'salary', 'leave', 'performance', 'training', 'termination']
        employment_types = ['Full-time', 'Part-time', 'Contract', 'Casual']
        statuses = ['active', 'inactive', 'pending', 'completed']
        approval_statuses = ['pending', 'approved', 'rejected']
        
        departments = list(Department.objects.all())
        
        for i in range(count):
            department = random.choice(departments)
            record_type = random.choice(record_types)
            
            # 生成员工信息
            employee_id = f"EMP-{random.randint(10000, 99999)}"
            employee_name = f"Employee {i+1}"
            position = f"Position {random.randint(1, 10)}"
            
            # 生成日期
            start_date = date.today() - timedelta(days=random.randint(0, 1000))
            end_date = start_date + timedelta(days=random.randint(30, 1000)) if random.random() > 0.7 else None
            
            # 生成数值信息
            amount = Decimal(random.uniform(50000, 150000)).quantize(Decimal('0.01')) if record_type == 'salary' else None
            days = random.randint(1, 30) if record_type == 'leave' else None
            
            HRRecord.objects.create(
                record_type=record_type,
                department=department,
                employee_id=employee_id,
                employee_name=employee_name,
                position=position,
                employment_type=random.choice(employment_types),
                description=f"Sample {record_type} record for {employee_name}",
                start_date=start_date,
                end_date=end_date,
                amount=amount,
                days=days,
                status=random.choice(statuses),
                approval_status=random.choice(approval_statuses),
                source_document=f"hr_document_{i+1}.pdf",
                created_by=f"hr_user_{random.randint(1, 5)}"
            )
        
        self.stdout.write(f'👥 创建了 {count} 条人力资源记录')

    def _populate_procurement_records(self, count: int, force: bool):
        """填充采购记录"""
        if force:
            ProcurementRecord.objects.all().delete()
            self.stdout.write('🗑️  清空现有采购记录')
        
        record_types = ['purchase_order', 'contract', 'tender', 'supplier_evaluation', 'delivery', 'payment']
        categories = ['IT Services', 'Office Supplies', 'Professional Services', 'Construction', 'Transport', 'Consulting']
        subcategories = ['Software', 'Hardware', 'Training', 'Maintenance', 'Support', 'Development']
        statuses = ['active', 'completed', 'cancelled', 'pending']
        approval_statuses = ['pending', 'approved', 'rejected']
        
        departments = list(Department.objects.all())
        
        for i in range(count):
            department = random.choice(departments)
            record_type = random.choice(record_types)
            
            # 生成合同信息
            contract_number = f"CON-{record_type.upper()}-{timezone.now().strftime('%Y%m')}-{i+1:04d}"
            supplier_name = f"Supplier Company {i+1} Pty Ltd"
            supplier_abn = f"{random.randint(10000000000, 99999999999)}" if random.random() > 0.3 else ""
            
            # 生成合同价值
            contract_value = Decimal(random.uniform(10000, 5000000)).quantize(Decimal('0.01'))
            
            # 生成日期
            start_date = date.today() - timedelta(days=random.randint(0, 500))
            end_date = start_date + timedelta(days=random.randint(30, 1000))
            
            # 选择类别
            category = random.choice(categories)
            subcategory = random.choice(subcategories) if random.random() > 0.5 else ""
            
            ProcurementRecord.objects.create(
                record_type=record_type,
                department=department,
                contract_number=contract_number,
                supplier_name=supplier_name,
                supplier_abn=supplier_abn,
                description=f"Sample {record_type} for {category} services",
                contract_value=contract_value,
                start_date=start_date,
                end_date=end_date,
                category=category,
                subcategory=subcategory,
                status=random.choice(statuses),
                approval_status=random.choice(approval_statuses),
                source_document=f"procurement_document_{i+1}.pdf",
                created_by=f"procurement_user_{random.randint(1, 5)}"
            )
        
        self.stdout.write(f'📦 创建了 {count} 条采购记录')
