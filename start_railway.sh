#!/bin/bash

# Railway专用启动脚本
echo "🚂 启动Railway FAQ后端服务..."

# 检查环境变量
echo "🔍 检查环境变量..."
if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  警告: DATABASE_URL未设置，将使用默认配置"
else
    echo "✅ DATABASE_URL已设置"
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  警告: OPENAI_API_KEY未设置，AI功能将不可用"
else
    echo "✅ OPENAI_API_KEY已设置"
fi

# 安装依赖
echo "📦 安装Python依赖..."
pip install -r requirements.txt

# 等待数据库就绪
echo "⏳ 等待Railway PostgreSQL数据库就绪..."
sleep 5

# 启动应用
echo "🚀 启动Flask应用..."
python app.py
