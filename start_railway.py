#!/usr/bin/env python3
"""
Railway专用启动脚本
确保Flask应用在Railway环境中正确启动
"""

import os
import sys
from app import app

def migrate_sqlite_data():
    """迁移SQLite数据到PostgreSQL"""
    try:
        print("🔄 开始迁移SQLite数据到PostgreSQL...")
        
        # 检查是否有SQLite数据库文件
        if os.path.exists('faq.db'):
            print("📁 发现SQLite数据库文件，开始迁移...")
            
            # 导入迁移模块
            from migrate_sqlite_to_postgresql import export_sqlite_data, import_to_postgresql
            
            # 导出数据
            if export_sqlite_data():
                print("✅ SQLite数据导出成功")
                
                # 导入到PostgreSQL
                if import_to_postgresql():
                    print("✅ 数据迁移完成")
                    return True
                else:
                    print("❌ PostgreSQL导入失败")
            else:
                print("❌ SQLite数据导出失败")
        else:
            print("ℹ️ 没有找到SQLite数据库文件，跳过迁移")
            
    except Exception as e:
        print(f"⚠️ 数据迁移失败: {e}")
        print("应用将继续启动，但可能没有数据")
    
    return False

def import_initial_data():
    """导入初始数据"""
    try:
        from import_data_railway import main as import_data
        print("📊 开始导入初始数据...")
        import_data()
        print("✅ 数据导入完成")
    except Exception as e:
        print(f"⚠️ 数据导入失败: {e}")
        print("应用将继续启动，但数据库可能为空")

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
    
    # 尝试迁移SQLite数据
    migration_success = migrate_sqlite_data()
    
    # 如果迁移失败，导入示例数据
    if not migration_success:
        print("📊 迁移失败，导入示例数据...")
        import_initial_data()
    
    try:
        # 启动Flask应用
        app.run(host=host, port=port, debug=debug)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
