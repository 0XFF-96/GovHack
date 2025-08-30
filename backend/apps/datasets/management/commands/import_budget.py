import csv
import time
import uuid
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from ...models import Portfolio, Department, Outcome, Program, BudgetExpense, DataImportLog


class Command(BaseCommand):
    help = '导入澳大利亚政府预算数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='CSV文件路径（默认: datasets/2024-25-pbs-program-expense-line-items.csv）'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='批处理大小（默认: 100）'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='预演模式，不实际导入数据'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='导入前清空现有数据'
        )

    def handle(self, *args, **options):
        # 参数设置
        file_path = options.get('file') or '/app/datasets/2024-25-pbs-program-expense-line-items.csv'
        batch_size = options.get('batch_size', 100)
        dry_run = options.get('dry_run', False)
        clear_data = options.get('clear', False)

        if dry_run:
            self.stdout.write(self.style.WARNING('⚠️  预演模式：不会实际导入数据'))

        # 创建导入日志
        batch_id = f'budget_import_{int(time.time())}'
        import_log = DataImportLog.objects.create(
            batch_id=batch_id,
            source_file=file_path,
            status='started',
            start_time=timezone.now()
        )

        try:
            self.stdout.write('开始导入预算数据...')
            self.stdout.write(f'批次ID: {batch_id}')
            self.stdout.write(f'文件路径: {file_path}')
            self.stdout.write(f'批处理大小: {batch_size}')
            self.stdout.write(f'预演模式: {dry_run}')
            self.stdout.write(f'清空数据: {clear_data}')

            # 清空现有数据
            if clear_data and not dry_run:
                self.stdout.write('清空现有数据...')
                BudgetExpense.objects.all().delete()
                Program.objects.all().delete()
                Outcome.objects.all().delete()
                Department.objects.all().delete()
                Portfolio.objects.all().delete()
                self.stdout.write(self.style.SUCCESS('数据清空完成'))

            # 解析CSV文件（处理编码问题）
            try:
                with open(file_path, 'r', encoding='utf-8') as csvfile:
                    content = csvfile.read()
            except UnicodeDecodeError:
                # 尝试使用Windows-1252编码（常见的Excel导出编码）
                with open(file_path, 'r', encoding='cp1252') as csvfile:
                    content = csvfile.read()
            
            # 将内容转换为UTF-8并处理
            from io import StringIO
            csvfile = StringIO(content)
            
            # 检测CSV方言
            sample = csvfile.read(1024)
            csvfile.seek(0)
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample)
            
            reader = csv.DictReader(csvfile, dialect=dialect)
            
            # 验证CSV头部
            required_fields = [
                'Portfolio', 'Department/Agency', 'Outcome', 'Program', 
                'Expense type', 'Appropriation type', 'Description',
                '2023-24', '2024-25', '2025-26', '2026-27', '2027-28'
            ]
            
            missing_fields = [field for field in required_fields if field not in reader.fieldnames]
            if missing_fields:
                raise CommandError(f'CSV文件缺少必需字段: {missing_fields}')

            # 统计总行数
            total_rows = sum(1 for _ in reader)
            csvfile.seek(0)
            reader = csv.DictReader(csvfile, dialect=dialect)  # 重新创建reader
            
            import_log.total_rows = total_rows
            import_log.status = 'processing'
            import_log.save()

            self.stdout.write(f'总计 {total_rows} 行数据')

            # 缓存对象以避免重复创建
            portfolios = {}
            departments = {}
            outcomes = {}
            programs = {}
            
            batch_data = []
            processed_rows = 0
            success_rows = 0
            error_rows = 0

            for row_num, row in enumerate(reader, start=1):
                try:
                    # 数据清洗和验证
                    cleaned_row = self.clean_row_data(row)
                    
                    if not cleaned_row:
                        error_rows += 1
                        continue

                    # 获取或创建Portfolio
                    portfolio_name = cleaned_row['portfolio']
                    if portfolio_name not in portfolios:
                        if not dry_run:
                            portfolio, created = Portfolio.objects.get_or_create(
                                name=portfolio_name,
                                defaults={'description': f'Portfolio for {portfolio_name}'}
                            )
                            portfolios[portfolio_name] = portfolio
                        else:
                            portfolios[portfolio_name] = None

                    # 获取或创建Department
                    dept_key = f"{portfolio_name}|{cleaned_row['department']}"
                    if dept_key not in departments:
                        if not dry_run:
                            department, created = Department.objects.get_or_create(
                                portfolio=portfolios[portfolio_name],
                                name=cleaned_row['department'],
                                defaults={'department_type': 'Agency'}
                            )
                            departments[dept_key] = department
                        else:
                            departments[dept_key] = None

                    # 获取或创建Outcome
                    outcome_key = f"{dept_key}|{cleaned_row['outcome']}"
                    if outcome_key not in outcomes:
                        if not dry_run:
                            # 提取outcome编号
                            outcome_parts = cleaned_row['outcome'].split(':', 1)
                            outcome_number = outcome_parts[0].strip() if outcome_parts else 'Outcome 1'
                            outcome_desc = outcome_parts[1].strip() if len(outcome_parts) > 1 else cleaned_row['outcome']
                            
                            outcome, created = Outcome.objects.get_or_create(
                                department=departments[dept_key],
                                outcome_number=outcome_number,
                                defaults={'description': outcome_desc}
                            )
                            outcomes[outcome_key] = outcome
                        else:
                            outcomes[outcome_key] = None

                    # 获取或创建Program
                    program_key = f"{outcome_key}|{cleaned_row['program']}"
                    if program_key not in programs:
                        if not dry_run:
                            # 提取program编号和名称
                            program_parts = cleaned_row['program'].split(' ', 1)
                            program_number = program_parts[0] if program_parts else 'Program 1'
                            program_name = program_parts[1] if len(program_parts) > 1 else cleaned_row['program']
                            
                            # 截断字段以避免超长
                            program_name = program_name[:400] if program_name else program_name
                            program_desc = cleaned_row['program'][:1000] if cleaned_row['program'] else ''
                            
                            # 使用完整的program描述作为唯一键以避免冲突
                            unique_program_number = f"{program_number}_{hash(cleaned_row['program']) % 10000:04d}"
                            
                            program, created = Program.objects.get_or_create(
                                department=departments[dept_key],
                                outcome=outcomes[outcome_key],
                                program_number=unique_program_number[:20],  # 确保不超过字段长度
                                defaults={
                                    'name': program_name,
                                    'description': program_desc
                                }
                            )
                            programs[program_key] = program
                        else:
                            programs[program_key] = None

                    # 准备BudgetExpense数据
                    if not dry_run:
                        budget_expense = BudgetExpense(
                            portfolio=portfolios[portfolio_name],
                            department=departments[dept_key],
                            outcome=outcomes[outcome_key],
                            program=programs[program_key],
                            expense_type=cleaned_row['expense_type'],
                            appropriation_type=cleaned_row['appropriation_type'],
                            description=cleaned_row['description'],
                            amount_2023_24=cleaned_row.get('amount_2023_24'),
                            amount_2024_25=cleaned_row.get('amount_2024_25'),
                            amount_2025_26=cleaned_row.get('amount_2025_26'),
                            amount_2026_27=cleaned_row.get('amount_2026_27'),
                            amount_2027_28=cleaned_row.get('amount_2027_28'),
                            source_document=row.get('Source document', ''),
                        )
                        batch_data.append(budget_expense)

                    processed_rows += 1
                    success_rows += 1

                    # 批量插入
                    if not dry_run and len(batch_data) >= batch_size:
                        BudgetExpense.objects.bulk_create(batch_data)
                        batch_data = []
                        self.stdout.write(f'已处理 {processed_rows}/{total_rows} 行')

                except Exception as e:
                    error_rows += 1
                    self.stderr.write(f'第{row_num}行错误: {str(e)}')
                    if error_rows > 10:  # 限制错误输出
                        self.stderr.write(f'错误过多，只显示前10个错误')
                        break

            # 处理剩余的批次数据
            if not dry_run and batch_data:
                BudgetExpense.objects.bulk_create(batch_data)

            # 更新导入日志
            import_log.end_time = timezone.now()
            import_log.processed_rows = processed_rows
            import_log.success_rows = success_rows
            import_log.error_rows = error_rows
            import_log.status = 'completed' if error_rows == 0 else 'completed'
            import_log.duration_seconds = (import_log.end_time - import_log.start_time).total_seconds()
            import_log.import_summary = {
                'portfolios_created': len(portfolios),
                'departments_created': len(departments),
                'outcomes_created': len(outcomes),
                'programs_created': len(programs),
                'total_processed': processed_rows,
                'success_rate': success_rows / processed_rows if processed_rows > 0 else 0
            }
            import_log.save()

            # 输出结果
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('=== 导入完成 ==='))
            self.stdout.write(f'总行数: {total_rows}')
            self.stdout.write(f'处理行数: {processed_rows}')
            self.stdout.write(f'成功行数: {success_rows}')
            self.stdout.write(f'错误行数: {error_rows}')
            self.stdout.write(f'成功率: {(success_rows/processed_rows*100):.1f}%' if processed_rows > 0 else '0.0%')
            self.stdout.write(f'创建Portfolio: {len(portfolios)}个')
            self.stdout.write(f'创建Department: {len(departments)}个')
            self.stdout.write(f'创建Outcome: {len(outcomes)}个')
            self.stdout.write(f'创建Program: {len(programs)}个')
            
            if dry_run:
                self.stdout.write(self.style.WARNING('(预演模式，未实际导入)'))

        except Exception as e:
            import_log.status = 'failed'
            import_log.end_time = timezone.now()
            import_log.save()
            raise CommandError(f'导入失败: {str(e)}')

    def clean_row_data(self, row):
        """清洗和验证行数据"""
        try:
            # 基本字段清洗（加上字符长度限制）
            cleaned = {
                'portfolio': self.clean_text(row.get('Portfolio', ''), max_length=200),
                'department': self.clean_text(row.get('Department/Agency', ''), max_length=300),
                'outcome': self.clean_text(row.get('Outcome', ''), max_length=500),
                'program': self.clean_text(row.get('Program', ''), max_length=400),
                'expense_type': self.clean_text(row.get('Expense type', ''), max_length=100),
                'appropriation_type': self.clean_text(row.get('Appropriation type', ''), max_length=150),
                'description': self.clean_text(row.get('Description', ''), max_length=1000),
            }
            
            # 金额字段清洗
            for year in ['2023-24', '2024-25', '2025-26', '2026-27', '2027-28']:
                amount_str = row.get(year, '').strip()
                cleaned[f'amount_{year.replace("-", "_")}'] = self.clean_amount(amount_str)
            
            # 验证必需字段
            if not all([cleaned['portfolio'], cleaned['department'], cleaned['program']]):
                return None
            
            return cleaned
            
        except Exception as e:
            return None

    def clean_text(self, text, max_length=None):
        """清洗文本字段"""
        if not text:
            return ''
        cleaned = str(text).strip().replace('\\n', ' ').replace('\\r', '')
        if max_length and len(cleaned) > max_length:
            cleaned = cleaned[:max_length]
        return cleaned

    def clean_amount(self, amount_str):
        """清洗金额字段"""
        if not amount_str or amount_str.strip() in ['', '-', 'N/A', 'n/a']:
            return None
        
        try:
            # 移除货币符号和逗号
            cleaned = amount_str.replace('$', '').replace(',', '').strip()
            if not cleaned:
                return None
            
            # 处理负号
            is_negative = cleaned.startswith('-') or cleaned.startswith('(')
            cleaned = cleaned.replace('-', '').replace('(', '').replace(')', '')
            
            # 转换为Decimal
            amount = Decimal(cleaned)
            if is_negative:
                amount = -amount
            
            return amount
            
        except (ValueError, InvalidOperation):
            return None