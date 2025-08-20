#!/usr/bin/env python3
"""
Railway专用启动脚本
确保Flask应用在Railway环境中正确启动
"""

import os
import sys
from app import app

def main():
    """主启动函数"""
    # Railway环境配置
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']
    
    # 在Railway上使用0.0.0.0绑定所有接口
    host = '0.0.0.0'
    
    print("🚂 启动Railway FAQ后端服务...")
    print(f"🌐 主机: {host}")
    print(f"🔌 端口: {port}")
    print(f"🐛 调试模式: {debug}")
    print(f"🗄️ 数据库: {os.environ.get('DATABASE_URL', 'Not set')[:50]}...")
    print(f"🤖 OpenAI: {'Configured' if os.environ.get('OPENAI_API_KEY') else 'Not configured'}")
    
    try:
        # 启动Flask应用
        app.run(host=host, port=port, debug=debug)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
