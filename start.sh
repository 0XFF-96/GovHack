#!/bin/bash

# GovHack项目启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 GovHack项目启动脚本${NC}"
echo -e "${BLUE}============================${NC}"

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker未运行，请先启动Docker${NC}"
    exit 1
fi

# 检查docker-compose是否可用
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose未安装${NC}"
    exit 1
fi

# 解析命令行参数
ACTION=${1:-"up"}

case $ACTION in
    "up"|"start")
        echo -e "${GREEN}🔧 启动服务...${NC}"
        
        # 构建并启动服务
        docker-compose up --build -d
        
        echo -e "${YELLOW}⏳ 等待服务启动...${NC}"
        sleep 10
        
        # 检查服务状态
        echo -e "${BLUE}📊 服务状态:${NC}"
        docker-compose ps
        
        echo -e "${GREEN}✅ 服务启动完成！${NC}"
        echo -e "${BLUE}📋 可用服务:${NC}"
        echo -e "  🌐 Swagger文档: http://localhost:8000/api/docs/"
        echo -e "  📖 ReDoc文档:   http://localhost:8000/api/redoc/"
        echo -e "  🔍 健康检查:     http://localhost:8000/api/health/"
        echo -e "  🛡️ Django管理:  http://localhost:8000/admin/"
        echo -e "  🗃️ 数据库:       localhost:5432"
        echo -e "  🚀 Redis:       localhost:6379"
        ;;
        
    "dev"|"develop")
        echo -e "${GREEN}🔧 启动开发环境 (热重载)...${NC}"
        
        # 使用开发配置启动
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
        ;;
        
    "dev-bg"|"dev-background")
        echo -e "${GREEN}🔧 后台启动开发环境...${NC}"
        
        # 后台模式启动开发环境
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d
        
        echo -e "${YELLOW}⏳ 等待开发服务启动...${NC}"
        sleep 8
        
        echo -e "${BLUE}📊 开发环境状态:${NC}"
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml ps
        
        echo -e "${GREEN}✅ 开发环境启动完成！${NC}"
        echo -e "${BLUE}📋 开发服务:${NC}"
        echo -e "  🌐 Django开发服务器: http://localhost:8000/"
        echo -e "  🗃️ 开发数据库:       localhost:5433"
        echo -e "  🚀 开发Redis:        localhost:6380"
        echo -e ""
        echo -e "${YELLOW}💡 提示: 修改代码后服务会自动重载${NC}"
        ;;
        
    "import"|"load-data")
        echo -e "${GREEN}📊 导入预算数据...${NC}"
        
        # 确保服务正在运行
        docker-compose up -d web
        
        # 等待服务启动
        echo -e "${YELLOW}⏳ 等待Django服务启动...${NC}"
        sleep 15
        
        # 运行数据导入
        docker-compose exec web python manage.py import_budget --clear
        
        echo -e "${GREEN}✅ 数据导入完成！${NC}"
        ;;
        
    "logs")
        echo -e "${BLUE}📋 查看服务日志...${NC}"
        docker-compose logs -f ${2:-"web"}
        ;;
        
    "shell")
        echo -e "${BLUE}🐍 进入Django shell...${NC}"
        docker-compose exec web python manage.py shell
        ;;
        
    "migrate")
        echo -e "${GREEN}🗃️ 执行数据库迁移...${NC}"
        docker-compose exec web python manage.py makemigrations
        docker-compose exec web python manage.py migrate
        ;;
        
    "test")
        echo -e "${GREEN}🧪 运行Django测试...${NC}"
        docker-compose exec web python manage.py test
        ;;
        
    "test-api")
        echo -e "${GREEN}🌐 测试API端点...${NC}"
        ./test-api.sh
        ;;
        
    "test-swagger")
        echo -e "${GREEN}📄 测试Swagger文档...${NC}"
        docker-compose exec web python manage.py test_swagger
        ;;
        
    "down"|"stop")
        echo -e "${RED}🛑 停止服务...${NC}"
        docker-compose down
        echo -e "${GREEN}✅ 服务已停止${NC}"
        ;;
        
    "clean")
        echo -e "${RED}🧹 清理Docker资源...${NC}"
        docker-compose down -v --remove-orphans
        docker system prune -f
        echo -e "${GREEN}✅ 清理完成${NC}"
        ;;
        
    "status")
        echo -e "${BLUE}📊 服务状态:${NC}"
        docker-compose ps
        echo ""
        echo -e "${BLUE}🌐 访问地址:${NC}"
        echo -e "  Swagger: http://localhost:8000/api/docs/"
        echo -e "  Health:  http://localhost:8000/api/health/"
        ;;
        
    "help"|"--help"|"-h")
        echo -e "${BLUE}使用方法: $0 [命令]${NC}"
        echo ""
        echo -e "${YELLOW}服务管理:${NC}"
        echo -e "  up, start     - 启动生产环境服务"
        echo -e "  dev           - 启动开发环境 (前台+热重载)"
        echo -e "  dev-bg        - 启动开发环境 (后台+热重载)"
        echo -e "  down, stop    - 停止服务"
        echo -e "  status        - 查看服务状态"
        echo ""
        echo -e "${YELLOW}数据管理:${NC}"
        echo -e "  import        - 导入预算数据"
        echo -e "  migrate       - 执行数据库迁移"
        echo ""
        echo -e "${YELLOW}开发调试:${NC}"
        echo -e "  logs [服务]   - 查看服务日志"
        echo -e "  shell         - 进入Django shell"
        echo -e "  test          - 运行Django测试"
        echo -e "  test-api      - 测试API端点"
        echo -e "  test-swagger  - 测试Swagger文档"
        echo ""
        echo -e "${YELLOW}维护工具:${NC}"
        echo -e "  clean         - 清理Docker资源"
        echo -e "  help          - 显示此帮助信息"
        echo ""
        echo -e "${BLUE}开发环境特性:${NC}"
        echo -e "  ✅ 代码热重载 - 修改后自动重启"
        echo -e "  ✅ 调试模式   - 详细错误信息"
        echo -e "  ✅ 快速启动   - 跳过健康检查"
        echo -e "  ✅ 独立端口   - 避免生产环境冲突"
        ;;
        
    *)
        echo -e "${RED}❌ 未知命令: $ACTION${NC}"
        echo -e "${YELLOW}使用 '$0 help' 查看可用命令${NC}"
        exit 1
        ;;
esac