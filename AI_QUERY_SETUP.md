# 🤖 AI 查询系统设置指南

我已经基于现有项目创建了一个完整的 AI 查询界面，类似于您提供的截图。

## 🎯 功能特色

### ✨ 已实现的功能

- **🗣️ 自然语言查询**: 支持中英文自然语言输入
- **🧠 智能路由**: 自动判断 SQL 查询 vs RAG 检索
- **📊 结构化响应**: 包含执行的 SQL、数据源、置信度等
- **📋 证据包面板**: 完整的审计追踪和元数据
- **🎨 现代化界面**: 基于 shadcn/ui 的精美界面
- **🔄 实时响应**: 支持加载状态和错误处理

### 🔌 集成特色

- **OpenAI GPT-3.5**: 用于查询意图分析
- **Django ORM**: 直接查询真实政府预算数据
- **Langchain Ready**: 预留 Langchain 集成接口
- **审计追踪**: 完整的操作记录和数据溯源

## 🚀 快速启动

### 1. 启动后端服务

```bash
cd /Users/li/go/src/github.com/GovHack
./start.sh dev-bg
```

### 2. 设置 OpenAI API 密钥 (可选)

```bash
# 在环境变量中设置
export OPENAI_API_KEY="your-openai-api-key-here"

# 或在Docker环境中设置
echo "OPENAI_API_KEY=your-openai-api-key-here" >> .env
```

### 3. 启动前端服务

```bash
cd frontend
npm run dev
```

### 4. 访问 AI 查询界面

打开浏览器访问: http://localhost:3000/query

## 🎮 使用示例

### 📊 SQL 查询示例

```
"What is the total education budget for 2024?"
"Compare department budgets"
"Show top 10 highest expenses"
"Average salary by department"
```

### 🔍 RAG 查询示例

```
"Find details about John Smith's employment record"
"Tell me about the Defence department structure"
"What programs are under Health portfolio?"
```

## 🏗️ 技术架构

### 前端组件

- **页面**: `frontend/app/query/page.tsx`
- **布局**: 更新了 `budget-layout.tsx` 添加 AI Query 导航
- **API**: 集成现有的 `api.chat.sendMessage()`

### 后端服务

- **AI 服务**: `backend/apps/chat/ai_service.py`
- **视图更新**: `backend/apps/chat/views.py`
- **依赖**: 添加了 openai、langchain 到 requirements.txt

### 🔄 数据流

```
用户查询 → 前端 → Django API → AI服务 →
OpenAI分析 → 数据库查询 → 结构化响应 → 前端展示
```

## ⚙️ 配置选项

### OpenAI 配置

```python
# backend/apps/chat/ai_service.py
openai.api_key = os.getenv('OPENAI_API_KEY', 'your-key-here')
```

### 查询参数调整

```python
# 在ai_service.py中可以调整:
- model="gpt-3.5-turbo"  # 可改为gpt-4
- temperature=0.1       # 控制创造性
- max_tokens=500        # 响应长度
```

## 🧪 测试查询

### 1. 基础功能测试

```bash
# 测试后端健康检查
curl http://localhost:8000/api/health/

# 测试聊天API
curl -X POST http://localhost:8000/api/v1/chat/query/ \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the total education budget for 2024?"}'
```

### 2. 前端界面测试

- 打开 http://localhost:3000/query
- 输入测试查询："What is the total education budget for 2024?"
- 检查响应格式和 Evidence Package 面板

## 🎨 界面特色

### 三栏布局

1. **左侧栏**: 导航菜单 + 查询历史
2. **主区域**: 查询输入 + 结果展示
3. **右侧栏**: Evidence Package + 审计信息

### 智能指示器

- 🟢 **SQL**: 数值统计、汇总、排序查询
- 🟡 **RAG**: 具体记录、详细信息查询

### 可信度系统

- **0.9-1.0**: 高置信度 - 直接数据查询
- **0.7-0.9**: 中等置信度 - 计算推导结果
- **0.5-0.7**: 较低置信度 - 有限数据可用
- **0.0-0.5**: 低置信度 - 推测性结果

## 🔧 定制化选项

### 1. 添加新的查询类型

在 `ai_service.py` 中添加新的处理方法:

```python
def _process_custom_query(self, query: str, intent: Dict) -> Dict:
    # 您的自定义逻辑
    pass
```

### 2. 集成更多 AI 模型

```python
# 可以添加Langchain集成
from langchain.llms import OpenAI
from langchain.chains import LLMChain

llm = OpenAI(temperature=0)
chain = LLMChain(llm=llm, prompt=prompt_template)
```

### 3. 扩展数据源

在 `ai_service.py` 中添加更多数据库查询:

```python
# 查询其他政府数据表
from apps.other_app.models import OtherModel
```

## 🚨 故障排除

### 常见问题

1. **OpenAI API 错误**

   - 检查 API 密钥是否正确设置
   - 系统会回退到基于规则的分析

2. **前端 API 调用失败**

   - 确认后端服务运行在 8000 端口
   - 检查 CORS 配置

3. **数据库查询错误**
   - 确认数据已导入: `./start.sh import`
   - 检查数据库连接状态

### 日志查看

```bash
# 查看Django日志
./start.sh logs web

# 查看前端控制台
# 打开浏览器开发者工具
```

## 🎯 下一步扩展

### 短期改进

- [ ] 添加更多查询模板
- [ ] 支持图表可视化
- [ ] 增强错误处理

### 中期功能

- [ ] 集成 Langchain 文档检索
- [ ] 添加查询建议系统
- [ ] 实现用户偏好设置

### 长期愿景

- [ ] 多轮对话支持
- [ ] 自定义报表生成
- [ ] 智能数据发现

## 📞 技术支持

如有问题或需要进一步定制，请参考:

- 项目文档: `/Users/li/go/src/github.com/GovHack/README.md`
- API 文档: http://localhost:8000/api/docs/
- 组件文档: `frontend/components/` 目录

---

🎉 **恭喜！您现在拥有一个功能完整的政府数据 AI 查询系统！**
