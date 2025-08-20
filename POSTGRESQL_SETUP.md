# PostgreSQL 配置指南

本应用现在完全使用 PostgreSQL 数据库，不再支持 SQLite。本指南将帮助您正确配置 PostgreSQL 连接。

## 🔧 环境要求

- Python 3.8+
- PostgreSQL 12+ (推荐使用 Azure Database for PostgreSQL)
- 所有依赖项已安装 (`pip install -r requirements.txt`)

## 📋 配置步骤

### 1. 环境变量配置

复制并编辑环境变量文件：

```bash
cp .env.example .env
```

### 2. 数据库连接配置

您有两种配置方式：

#### 方式一：使用完整连接字符串（推荐）

在 `.env` 文件中设置：

```env
DATABASE_URL=postgresql://username:password@hostname:5432/database_name?sslmode=require
```

#### 方式二：使用独立变量

在 `.env` 文件中设置：

```env
POSTGRES_HOST=your-server-name.postgres.database.azure.com
POSTGRES_PORT=5432
POSTGRES_DB=your-database-name
POSTGRES_USER=your-username
POSTGRES_PASSWORD=your-password
POSTGRES_SSLMODE=require
```

### 3. Azure PostgreSQL 配置示例

对于 Azure Database for PostgreSQL：

```env
# 使用连接字符串
DATABASE_URL=postgresql://myuser@myserver:mypassword@myserver.postgres.database.azure.com:5432/mydatabase?sslmode=require

# 或使用独立变量
POSTGRES_HOST=myserver.postgres.database.azure.com
POSTGRES_PORT=5432
POSTGRES_DB=mydatabase
POSTGRES_USER=myuser@myserver
POSTGRES_PASSWORD=mypassword
POSTGRES_SSLMODE=require
```

### 4. 其他必需的环境变量

```env
# OpenAI API 配置
OPENAI_API_KEY=your_openai_api_key_here

# Flask 配置
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secure-secret-key-here

# AI 服务配置
AI_SIMILARITY_THRESHOLD=0.3
AI_MAX_TOKENS=500
AI_TEMPERATURE=0.7
```

## 🧪 测试连接

### 1. 运行连接测试

```bash
python test_postgresql_connection.py
```

这个脚本将：
- 测试数据库连接
- 创建所有必需的表
- 执行基本的 CRUD 操作
- 验证配置是否正确

### 2. 启动应用程序

```bash
python app.py
```

应用程序将自动：
- 连接到 PostgreSQL 数据库
- 创建所有必需的表（如果不存在）
- 启动 Flask 服务器

## 📊 数据迁移

### 从 SQLite 迁移（如果需要）

如果您有现有的 SQLite 数据需要迁移：

```bash
python migrate_sqlite_to_postgresql.py
```

这个脚本将：
- 从 SQLite 数据库导出所有数据
- 将数据导入到 PostgreSQL
- 保持数据完整性

### 添加初始数据

如果您需要添加示例数据：

```bash
python sample_faqs.py
```

## 🔍 故障排除

### 常见问题

1. **连接超时**
   - 检查防火墙规则
   - 确认 SSL 设置正确
   - 验证服务器地址和端口

2. **认证失败**
   - 检查用户名和密码
   - 确认用户有数据库访问权限
   - 对于 Azure，确保用户名格式正确（`username@servername`）

3. **数据库不存在**
   - 确认数据库已在 PostgreSQL 服务器上创建
   - 检查数据库名称拼写

4. **SSL 连接问题**
   - 确保使用 `sslmode=require`
   - 检查服务器是否支持 SSL

### 调试步骤

1. **检查配置**
   ```bash
   python -c "from config import Config; print(Config().SQLALCHEMY_DATABASE_URI)"
   ```

2. **测试基本连接**
   ```bash
   python test_postgresql_connection.py
   ```

3. **查看详细错误**
   ```bash
   FLASK_DEBUG=True python app.py
   ```

## 🔒 安全最佳实践

1. **环境变量安全**
   - 不要将 `.env` 文件提交到版本控制
   - 使用强密码
   - 定期轮换密钥

2. **数据库安全**
   - 启用 SSL 连接
   - 限制数据库访问 IP
   - 使用最小权限原则

3. **生产环境**
   - 使用 Azure Key Vault 存储敏感信息
   - 启用数据库审计
   - 配置自动备份

## 📈 性能优化

1. **连接池配置**
   应用已配置连接池：
   ```python
   SQLALCHEMY_ENGINE_OPTIONS = {
       'pool_pre_ping': True,
       'pool_recycle': 300,
   }
   ```

2. **索引优化**
   - 为常用查询字段添加索引
   - 监控查询性能

3. **Azure 特定优化**
   - 使用适当的定价层
   - 启用连接池
   - 配置读取副本（如需要）

## 📞 支持

如果遇到问题：

1. 检查本文档的故障排除部分
2. 运行 `test_postgresql_connection.py` 进行诊断
3. 查看应用程序日志获取详细错误信息
4. 确认 Azure PostgreSQL 服务状态（如使用 Azure）

---

**注意**: 本应用不再支持 SQLite。如果您需要本地开发环境，请使用本地 PostgreSQL 实例或 Docker 容器。