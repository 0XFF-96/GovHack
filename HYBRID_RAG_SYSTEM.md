# 🤖 混合路由 RAG 系统

## 🎯 系统概述

这是一个基于 Django 的混合路由系统，将 SQL 查询和 RAG（检索增强生成）技术相结合，为政府数据提供智能查询服务。

### ✨ 核心特性

- **🔀 智能路由**: 自动判断查询类型（SQL/RAG/Hybrid）
- **📊 SQL 查询**: 处理数值统计、聚合、排序等结构化查询
- **🔍 RAG 检索**: 基于向量的文档检索和事实查证
- **🔄 混合查询**: 同时执行 SQL 和 RAG，提供全面分析
- **📋 证据包**: 完整的审计追踪和数据溯源
- **🎯 置信度评分**: 为每个查询结果提供可信度评估

## 🏗️ 系统架构

### 数据模型

```
📁 预算数据 (SQL查询)
├── Portfolio (部门组合)
├── Department (具体部门)
└── BudgetExpense (预算支出)

📁 业务数据 (RAG检索)
├── FinanceRecord (财务记录)
├── HRRecord (人力资源记录)
└── ProcurementRecord (采购记录)

📁 向量存储
└── DocumentVector (文档向量)
```

### 查询流程

```
用户查询 → 意图分析 → 路由判断 → 执行查询 → 结果合并 → 证据包生成
    ↓           ↓         ↓         ↓         ↓         ↓
  自然语言    OpenAI分析  智能选择   SQL/RAG   数据整合   审计追踪
```

## 🚀 快速开始

### 1. 环境准备

```bash
cd /Users/li/go/src/github.com/GovHack/backend
pip install -r requirements.txt
```

### 2. 数据库迁移

```bash
python manage.py makemigrations datasets
python manage.py migrate
```

### 3. 填充示例数据

```bash
# 创建 20 条示例记录
python manage.py populate_sample_data --count 20

# 强制重建所有数据
python manage.py populate_sample_data --count 50 --force
```

### 4. 文档向量化

```bash
# 执行向量化
python manage.py vectorize_documents

# 强制重建向量
python manage.py vectorize_documents --force

# 查看统计信息
python manage.py vectorize_documents --stats-only
```

### 5. 测试系统

```bash
python test_hybrid_system.py
```

## 🎮 使用示例

### SQL 查询示例

```python
# 预算统计查询
queries = [
    "What is the total education budget for 2024?",
    "Show me the top 10 highest expenses",
    "Compare department budgets",
    "What is the average budget by portfolio?",
    "How much does the health department spend?"
]
```

**预期结果**: 返回数值统计、图表数据、SQL 执行语句

### RAG 查询示例

```python
# 事实查证查询
queries = [
    "Find details about Supplier Company 1",
    "Tell me about Employee 1's employment record",
    "What contracts does the Health department have?",
    "Find the latest payment records",
    "Show me training records for employees"
]
```

**预期结果**: 返回相关文档、记录详情、相关性评分

### 混合查询示例

```python
# 综合分析查询
queries = [
    "How much does the education department spend and show me the details?",
    "What is the total budget and find related contracts?",
    "Show me budget summary and employee records",
    "Compare department spending and find supplier information"
]
```

**预期结果**: 同时返回统计信息和具体记录，提供全面分析

## 🔧 系统配置

### OpenAI 配置

```python
# 在环境变量中设置
export OPENAI_API_KEY="your-openai-api-key-here"

# 或在 Django 设置中配置
OPENAI_API_KEY = "your-openai-api-key-here"
```

### 向量化参数

```python
# 在 rag_service.py 中调整
class RAGService:
    def __init__(self):
        self.chunk_size = 1000      # 文档分块大小
        self.overlap = 200          # 分块重叠大小
        self.top_k = 5              # 检索结果数量
```

### 置信度计算

```python
# 在 ai_service.py 中调整
def _calculate_confidence(self, result: Dict) -> float:
    base_confidence = 0.5

    # 根据方法调整置信度
    if result.get('method') == 'SQL':
        base_confidence += 0.3      # SQL查询通常更可靠
    elif result.get('method') == 'RAG':
        base_confidence += 0.2      # RAG检索的可靠性
    elif result.get('method') == 'HYBRID':
        base_confidence += 0.4      # 混合查询最可靠

    return min(base_confidence, 1.0)
```

## 📊 性能优化

### 向量化优化

1. **批量处理**: 使用 `--force` 参数重建向量
2. **增量更新**: 只处理新增或修改的记录
3. **向量压缩**: 使用更高效的向量表示

### 查询优化

1. **缓存机制**: 缓存常用查询结果
2. **并行处理**: 混合查询并行执行 SQL 和 RAG
3. **结果分页**: 限制返回结果数量

### 数据库优化

1. **索引优化**: 为常用查询字段添加索引
2. **查询优化**: 使用 Django ORM 优化器
3. **连接池**: 配置数据库连接池

## 🧪 测试和调试

### 单元测试

```bash
# 运行所有测试
python manage.py test

# 运行特定应用测试
python manage.py test apps.chat
python manage.py test apps.datasets
```

### 集成测试

```bash
# 运行混合系统测试
python test_hybrid_system.py

# 测试特定功能
python manage.py shell
```

```python
from apps.chat.ai_service import AIQueryService
from apps.chat.rag_service import rag_service

# 测试 AI 服务
ai_service = AIQueryService()
result = ai_service.process_query("What is the total budget?")

# 测试 RAG 服务
results = rag_service.search_documents("supplier")
```

### 性能测试

```bash
# 测试向量化性能
time python manage.py vectorize_documents --force

# 测试查询性能
python -m cProfile -o profile.stats test_hybrid_system.py
```

## 🚨 故障排除

### 常见问题

1. **向量化失败**

   ```bash
   # 检查数据是否存在
   python manage.py vectorize_documents --stats-only

   # 重新填充数据
   python manage.py populate_sample_data --count 20
   ```

2. **OpenAI API 错误**

   ```bash
   # 检查 API 密钥
   echo $OPENAI_API_KEY

   # 系统会自动回退到基于规则的分析
   ```

3. **数据库连接错误**

   ```bash
   # 检查数据库状态
   python manage.py dbshell

   # 运行迁移
   python manage.py migrate
   ```

### 日志查看

```bash
# 查看 Django 日志
tail -f logs/django.log

# 查看应用日志
python manage.py shell
```

```python
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
```

## 🔮 未来扩展

### 短期改进

- [ ] 支持更多数据源
- [ ] 增强向量化算法
- [ ] 添加查询建议系统
- [ ] 实现结果缓存

### 中期功能

- [ ] 集成 Langchain 文档检索
- [ ] 添加多模态查询支持
- [ ] 实现用户偏好学习
- [ ] 支持自定义查询模板

### 长期愿景

- [ ] 实时数据流处理
- [ ] 分布式向量存储
- [ ] 多语言查询支持
- [ ] 智能报表生成