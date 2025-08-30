# GovHack Docker容器化指南

## 🚀 快速开始

### 一键启动
```bash
# 🔥 开发环境 (热重载)
./start.sh dev

# 或后台启动开发环境
./start.sh dev-bg

# 生产环境
./start.sh up

# 导入预算数据
./start.sh import

# 查看服务状态
./start.sh status
```

### 🔥 开发环境热重载
开发环境支持代码热重载，修改Python代码后会自动重启Django服务：

```bash
# 前台启动 (推荐开发时使用)
./start.sh dev

# 后台启动
./start.sh dev-bg
```

**开发环境特性**：
- ✅ **自动重载** - 代码修改后自动重启
- ✅ **调试模式** - 详细错误信息和堆栈跟踪
- ✅ **快速启动** - 跳过健康检查，启动更快
- ✅ **独立端口** - 避免与生产环境冲突
- ✅ **VSCode集成** - 完整的调试和开发支持

### 访问应用
- **Swagger API文档**: http://localhost:8000/api/docs/
- **ReDoc文档**: http://localhost:8000/api/redoc/
- **系统健康检查**: http://localhost:8000/api/health/
- **Django管理后台**: http://localhost:8000/admin/

## 📋 服务架构

| 服务 | 生产端口 | 开发端口 | 描述 |
|-----|---------|---------|------|
| `web` | 8000 | 8000 | Django API服务 |
| `db` | 5432 | 5433 | PostgreSQL数据库 |
| `redis` | 6379 | 6380 | Redis缓存 |
| `celery_worker` | - | - | 异步任务处理 |

### 🔧 开发vs生产环境

| 特性 | 开发环境 (`./start.sh dev`) | 生产环境 (`./start.sh up`) |
|-----|--------------------------|-------------------------|
| **热重载** | ✅ 自动重启 | ❌ 需要手动重启 |
| **调试模式** | ✅ DEBUG=True | ❌ DEBUG=False |
| **启动速度** | 🚀 快速 | 🐌 健康检查 |
| **端口** | 独立端口 | 标准端口 |
| **数据持久化** | 🔄 开发数据 | 💾 生产数据 |
| **性能优化** | ❌ 开发优先 | ✅ 生产优化 |

## 🔧 详细操作

### 启动服务
```bash
# 构建并启动所有服务
docker-compose up --build -d

# 仅启动特定服务
docker-compose up -d web db redis
```

### 数据库操作
```bash
# 执行数据库迁移
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# 创建超级用户
docker-compose exec web python manage.py createsuperuser

# 进入数据库shell
docker-compose exec db psql -U postgres -d govhack_db
```

### 数据导入
```bash
# 导入预算数据（清空现有数据）
docker-compose exec web python manage.py import_budget --clear

# 预演模式（不实际导入）
docker-compose exec web python manage.py import_budget --dry-run

# 自定义文件路径
docker-compose exec web python manage.py import_budget --file /app/datasets/custom.csv
```

### 开发调试
```bash
# 查看服务日志
docker-compose logs -f web

# 进入Django shell
docker-compose exec web python manage.py shell

# 运行测试
docker-compose exec web python manage.py test

# 进入容器bash
docker-compose exec web bash
```

### 服务管理
```bash
# 停止服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v

# 重启特定服务
docker-compose restart web

# 查看服务状态
docker-compose ps
```

## 🏗️ 项目结构

```
backend/
├── Dockerfile                 # Django应用容器镜像
├── requirements.txt           # Python依赖
├── .dockerignore             # Docker忽略文件
├── govhack_backend/          # Django项目配置
│   ├── settings.py           # 配置文件
│   ├── urls.py              # URL路由
│   └── api_schema.py        # Swagger配置
└── apps/                     # Django应用
    ├── datasets/            # 数据集管理
    ├── chat/                # 聊天对话
    ├── data_processing/     # 数据处理
    ├── trust_scoring/       # 信任评分
    ├── audit/               # 审计追踪
    └── health/              # 健康检查

docker-compose.yml            # 服务编排配置
start.sh                     # 启动脚本
```

## 🔍 API文档说明

### 核心API模块

1. **数据集管理** (`/api/v1/datasets/`)
   - 部门组合和部门查询
   - 预算数据搜索和统计
   - 数据导入状态监控

2. **聊天对话** (`/api/v1/chat/`)
   - AI对话会话管理
   - 自然语言查询处理
   - 信任度评分集成

3. **数据处理** (`/api/v1/data/`)
   - 数据集信息查询
   - 数据搜索和过滤

4. **信任评分** (`/api/v1/trust/`)
   - 查询结果信任度计算
   - 评分指标统计

5. **审计追踪** (`/api/v1/audit/`)
   - 操作日志记录
   - 用户活动统计

### 数据模型

- **Portfolio**: 部门组合 (如Attorney-General's)
- **Department**: 政府部门/机构
- **Program**: 具体项目
- **BudgetExpense**: 预算支出明细 (1,883条记录)

## 🛠️ 开发环境配置

### 环境变量
```env
# Django设置
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# 数据库
DB_NAME=govhack_db
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0
```

### 本地开发
```bash
# 克隆项目
git clone <repository>
cd GovHack

# 启动开发环境
./start.sh up

# 导入测试数据
./start.sh import

# 开发时实时查看日志
./start.sh logs web
```

## 🔧 故障排除

### 常见问题

1. **服务启动失败**
```bash
# 检查Docker是否运行
docker info

# 查看服务日志
docker-compose logs web

# 重新构建镜像
docker-compose build --no-cache web
```

2. **数据库连接错误**
```bash
# 检查数据库状态
docker-compose ps db

# 重启数据库
docker-compose restart db

# 查看数据库日志
docker-compose logs db
```

3. **数据导入失败**
```bash
# 检查数据文件是否存在
docker-compose exec web ls -la /app/datasets/

# 查看导入日志
docker-compose exec web python manage.py shell
>>> from apps.datasets.models import DataImportLog
>>> DataImportLog.objects.order_by('-created_at').first().error_message
```

4. **端口占用**
```bash
# 查看端口使用情况
lsof -i :8000
lsof -i :5432

# 修改docker-compose.yml中的端口映射
```

### 性能优化

1. **数据库优化**
```bash
# 查看数据库连接数
docker-compose exec db psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# 优化查询
docker-compose exec web python manage.py dbshell
```

2. **缓存配置**
```bash
# 查看Redis状态
docker-compose exec redis redis-cli info

# 清除缓存
docker-compose exec redis redis-cli flushall
```

## 📊 监控和日志

### 健康检查
```bash
# API健康检查
curl http://localhost:8000/api/health/

# 数据库健康检查
docker-compose exec db pg_isready -U postgres

# Redis健康检查
docker-compose exec redis redis-cli ping
```

### 日志查看
```bash
# 实时查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f web

# 查看最近的日志
docker-compose logs --tail=100 web
```

## 🚀 生产部署

### 生产环境配置
```bash
# 使用生产配置
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 启用Nginx
docker-compose --profile production up -d
```

### 安全考虑
- 修改默认密码和密钥
- 配置HTTPS证书
- 限制数据库访问
- 启用防火墙规则

---

📖 **完整文档**: 请查看 `backend/CLAUDE.md` 了解API详细说明