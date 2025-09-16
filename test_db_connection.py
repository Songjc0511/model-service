#!/usr/bin/env python3
"""
简单的数据库连接测试脚本
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

def test_database_connection():
    """测试数据库连接"""
    print("=== 数据库连接测试 ===")
    
    # 数据库URL配置
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://langchain:langchain@localhost:8001/langchain")
    print(f"数据库URL: {DATABASE_URL}")
    
    try:
        # 创建数据库引擎
        engine = create_engine(
            DATABASE_URL,
            echo=True,  # 开启SQL日志
            pool_pre_ping=True,
            pool_recycle=300,
        )
        
        print("正在测试数据库连接...")
        
        # 测试连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"✅ 数据库连接成功! 测试查询结果: {row[0]}")
            
            # 测试数据库版本
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ PostgreSQL版本: {version}")
            
            # 测试数据库名称
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"✅ 当前数据库: {db_name}")
            
        return True
        
    except OperationalError as e:
        print(f"❌ 数据库连接失败 (OperationalError): {e}")
        print("请检查:")
        print("1. PostgreSQL服务是否正在运行")
        print("2. 端口号是否正确 (8001)")
        print("3. 用户名和密码是否正确")
        print("4. 数据库是否存在")
        return False
        
    except Exception as e:
        print(f"❌ 数据库连接失败 (其他错误): {e}")
        return False

def test_docker_container():
    """检查Docker容器状态"""
    print("\n=== Docker容器检查 ===")
    import subprocess
    
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=pgvector-container", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("Docker容器状态:")
            print(result.stdout)
        else:
            print("❌ 无法获取Docker容器状态")
            print("请确保Docker正在运行，并且容器已启动")
            
    except FileNotFoundError:
        print("❌ 未找到Docker命令")
        print("请确保Docker已安装并在PATH中")
    except Exception as e:
        print(f"❌ 检查Docker容器时出错: {e}")

def main():
    """主函数"""
    print("开始数据库连接诊断...")
    
    # 检查Docker容器
    test_docker_container()
    
    # 测试数据库连接
    success = test_database_connection()
    
    if success:
        print("\n✅ 数据库连接测试成功!")
        print("现在可以运行完整的测试: python test_postgres.py")
    else:
        print("\n❌ 数据库连接测试失败!")
        print("请按照上述提示检查配置")

if __name__ == "__main__":
    main()
