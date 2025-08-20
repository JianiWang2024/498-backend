# Railway 部署指南

## 概述
本指南将帮助你将FAQ后端应用部署到Railway平台，并使用Railway PostgreSQL数据库。

## 前置条件
- Railway账号
- 已创建Railway项目
- 已创建PostgreSQL数据库服务

## 部署步骤

### 1. 创建Railway项目
1. 登录 [Railway](https://railway.app/)
2. 创建新项目
3. 选择"Deploy from GitHub repo"

### 2. 添加PostgreSQL服务
1. 在项目中点击"New Service"
2. 选择"Database" → "PostgreSQL"
3. 等待数据库创建完成

### 3. 配置环境变量
在Railway项目设置中添加以下环境变量：

#### 数据库配置
```
DATABASE_URL=postgresql://postgres:OTtJCXtjFmwTdYEBuEwXkMELBxTArGWT@postgres.railway.internal:5432/railway?sslmode=require
```

#### 或者分别设置
```
POSTGRES_HOST=postgres.railway.internal
POSTGRES_PORT=5432
POSTGRES_DB=railway
POSTGRES_USER=postgres
POSTGRES_PASSWORD=OTtJCXtjFmwTdYEBuEwXkMELBxTArGWT
POSTGRES_SSLMODE=require
```

#### 其他配置
```
RAILWAY_DEPLOYMENT=true
RAILWAY_APP_SERVICE=true
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secure-secret-key-here
OPENAI_API_KEY=your-openai-api-key-here
```

### 4. 部署应用
1. 连接GitHub仓库
2. 设置构建命令：`pip install -r requirements-railway.txt`
3. 设置启动命令：`python app.py`
4. 等待部署完成

### 5. 配置域名
1. 在Railway中获取应用URL
2. 配置自定义域名（可选）

## 配置说明

### 数据库连接
- 使用Railway内部域名：`postgres.railway.internal`
- 端口：5432
- 数据库名：railway
- 用户名：postgres
- 密码：OTtJCXtjFmwTdYEBuEwXkMELBxTArGWT

### 环境变量优先级
1. Railway环境变量（最高）
2. .env文件
3. 默认值（最低）

## 验证部署

### 1. 检查应用状态
- 在Railway仪表板查看应用状态
- 确认所有环境变量已设置

### 2. 测试API端点
- 健康检查：`/`
- FAQ API：`/api/faqs`
- 用户认证：`/api/login`

### 3. 检查数据库连接
- 查看应用日志
- 确认数据库表已创建

## 故障排除

### 常见问题

#### 1. 数据库连接失败
- 检查环境变量设置
- 确认PostgreSQL服务正在运行
- 检查网络连接

#### 2. 应用启动失败
- 检查构建命令
- 查看启动日志
- 确认依赖已安装

#### 3. 环境变量未生效
- 重新部署应用
- 检查变量名称格式
- 确认变量值正确

## 性能优化

### 1. 数据库连接池
```
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
```

### 2. 缓存策略
- 启用Redis缓存（可选）
- 优化数据库查询
- 使用CDN加速

## 监控和维护

### 1. 日志查看
- 在Railway仪表板查看应用日志
- 设置日志级别
- 监控错误和性能

### 2. 自动部署
- 配置GitHub Actions
- 设置自动测试
- 启用健康检查

## 联系支持
如果遇到问题：
1. 查看Railway文档
2. 检查应用日志
3. 联系Railway支持团队

---
*最后更新: 2024年*
