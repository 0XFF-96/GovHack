# 🔑 OpenAI API 设置指南

## 📋 获取 OpenAI API 密钥

### 1. 访问 OpenAI 官网

前往 https://platform.openai.com/api-keys

### 2. 创建账户并登录

- 注册 OpenAI 账户
- 验证邮箱和手机号

### 3. 创建 API 密钥

- 点击 "Create new secret key"
- 复制生成的密钥（格式：sk-xxxxxx）
- ⚠️ **重要**: 密钥只显示一次，请立即保存

## ⚙️ 配置 API 密钥

### 方法 1: 修改 Docker 配置（推荐）

1. **编辑 docker-compose.yml 文件**

```yaml
# 找到这一行并替换为您的真实API密钥
OPENAI_API_KEY: "sk-your-actual-api-key-here"
```

2. **重启服务**

```bash
./start.sh down
./start.sh dev-bg
```

### 方法 2: 环境变量设置

#### macOS/Linux:

```bash
# 临时设置（当前终端）
export OPENAI_API_KEY="sk-your-actual-api-key-here"

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export OPENAI_API_KEY="sk-your-actual-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

#### Windows:

```cmd
# 命令行设置
set OPENAI_API_KEY=sk-your-actual-api-key-here

# 或通过系统环境变量设置
```

### 方法 3: 创建.env 文件

1. **在项目根目录创建 .env 文件**

```bash
cd /Users/li/go/src/github.com/GovHack
touch .env
```

2. **编辑 .env 文件内容**

```
OPENAI_API_KEY=sk-your-actual-api-key-here
DEBUG=True
```

## 🧪 测试配置

### 1. 重启服务

```bash
./start.sh down
./start.sh dev-bg
```

### 2. 测试 API 调用

```bash
# 测试聊天接口
curl -X POST http://localhost:8000/api/v1/chat/query/ \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the total education budget for 2024?"}'
```

### 3. 前端测试

- 访问 http://localhost:3000/query
- 输入查询："What is the total education budget for 2024?"
- 检查是否返回智能分析结果

## 🚨 故障排除

### 问题 1: API 密钥无效

**错误信息**: "Invalid API key"
**解决方案**:

- 检查密钥格式是否正确（以 sk-开头）
- 确认密钥没有过期
- 验证账户余额是否充足

### 问题 2: 配置未生效

**症状**: 仍然显示模拟响应
**解决方案**:

```bash
# 1. 确认环境变量
echo $OPENAI_API_KEY

# 2. 重启Docker服务
./start.sh down
./start.sh dev-bg

# 3. 检查日志
./start.sh logs web
```

### 问题 3: 网络连接问题

**错误信息**: "Connection timeout"
**解决方案**:

- 检查网络连接
- 确认防火墙设置
- 尝试使用代理（如需要）

## 💡 无 API 密钥使用

**如果暂时没有 OpenAI API 密钥，系统会自动回退到基于规则的分析**

- 仍然可以处理基础查询
- 会显示"基于规则分析"的结果
- 功能有限但依然可用

## 💰 费用说明

### OpenAI API 定价（仅供参考）

- GPT-3.5-turbo: ~$0.002/1K tokens
- 每次查询通常消耗 50-200 tokens
- 预估成本：每 100 次查询约$0.01-0.04

### 免费额度

- 新用户通常有$5 免费额度
- 足够进行数千次测试查询

## 🔒 安全提醒

1. **保护 API 密钥**

   - 不要在代码中硬编码
   - 不要提交到 Git 仓库
   - 使用环境变量或配置文件

2. **监控使用量**

   - 定期检查 OpenAI 使用情况
   - 设置使用限额
   - 监控异常调用

3. **生产环境**
   - 使用专用 API 密钥
   - 启用 IP 白名单
   - 设置使用配额

## 📞 获取帮助

如果遇到问题，可以：

1. 查看 OpenAI 官方文档
2. 检查系统日志：`./start.sh logs web`
3. 访问 OpenAI 支持页面

---

🎉 **配置完成后，您就可以享受强大的 AI 查询功能了！**
