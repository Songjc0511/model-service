#!/usr/bin/env python3
"""
PostgreSQL连接和用户功能测试脚本
"""
import requests
import json
import asyncio
import websockets
from datetime import datetime

# 测试配置
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/api/v1/ws/chat"
USER_ID = "test_user_postgres"
CONVERSATION_ID = None

def test_database_connection():
    """测试数据库连接"""
    print("=== 测试PostgreSQL连接 ===")
    try:
        from model_service.db.database import engine
        from model_service.db.models import Base
        
        # 创建表
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库表创建成功")
        
        # 测试连接
        with engine.connect() as conn:
            from sqlalchemy import text
            result = conn.execute(text("SELECT 1"))
            print("✅ PostgreSQL连接成功")
            
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False
    
    return True

def test_user_api():
    """测试用户API"""
    print("\n=== 测试用户API ===")
    
    headers = {"X-User-ID": USER_ID}
    
    # 1. 获取当前用户信息（会自动创建用户）
    print("1. 获取当前用户信息...")
    response = requests.get(f"{BASE_URL}/api/v1/users/me", headers=headers)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        user_data = response.json()
        print(f"用户信息: {user_data['username']} - {user_data['description']}")
        print(f"响应频率: {user_data['response_frequency']}")
        print(f"总对话数: {user_data['total_conversations']}")
        print(f"总消息数: {user_data['total_messages']}")
    
    # 2. 更新用户信息
    print("\n2. 更新用户信息...")
    update_data = {
        "username": f"updated_user_{USER_ID}",
        "description": f"更新后的用户描述 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "response_frequency": 0.8,
        "preferences": {
            "language": "zh-CN",
            "theme": "dark",
            "notifications": True
        }
    }
    response = requests.put(f"{BASE_URL}/api/v1/users/me", headers=headers, json=update_data)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        user_data = response.json()
        print(f"更新后用户名: {user_data['username']}")
        print(f"更新后描述: {user_data['description']}")
        print(f"更新后偏好: {user_data['preferences']}")
    
    # 3. 获取用户统计信息
    print("\n3. 获取用户统计信息...")
    response = requests.get(f"{BASE_URL}/api/v1/users/me/stats", headers=headers)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        stats = response.json()
        print(f"统计信息: 对话数={stats['total_conversations']}, 消息数={stats['total_messages']}")
        print(f"平均响应频率: {stats['avg_response_frequency']}")
        print(f"最后活跃: {stats['last_active']}")
    
    # 4. 更新用户活跃时间
    print("\n4. 更新用户活跃时间...")
    response = requests.post(f"{BASE_URL}/api/v1/users/me/activity", headers=headers)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print("✅ 活跃时间更新成功")
    
    # 5. 搜索用户
    print("\n5. 搜索用户...")
    response = requests.get(f"{BASE_URL}/api/v1/users/search?q=test&limit=5")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        users = response.json()
        print(f"找到 {len(users)} 个用户")
        for user in users[:3]:
            print(f"  - {user['username']}: {user['description']}")

def test_chat_with_user_stats():
    """测试聊天功能并验证用户统计更新"""
    print("\n=== 测试聊天功能和用户统计 ===")
    
    # 创建对话
    headers = {"X-User-ID": USER_ID}
    response = requests.post(f"{BASE_URL}/api/v1/conversations", headers=headers)
    if response.status_code == 200:
        global CONVERSATION_ID
        CONVERSATION_ID = response.json()["conversation_id"]
        print(f"创建对话: {CONVERSATION_ID}")
    
    # 获取更新后的统计信息
    response = requests.get(f"{BASE_URL}/api/v1/users/me/stats", headers=headers)
    if response.status_code == 200:
        stats = response.json()
        print(f"对话后统计: 对话数={stats['total_conversations']}, 消息数={stats['total_messages']}")

async def test_websocket_with_user():
    """测试WebSocket连接和用户功能"""
    print("\n=== 测试WebSocket用户功能 ===")
    
    uri = f"{WS_URL}?user_id={USER_ID}"
    if CONVERSATION_ID:
        uri += f"&conversation_id={CONVERSATION_ID}"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("WebSocket连接已建立")
            
            # 发送文本消息
            message = {
                "type": "text",
                "data": "这是一条测试消息，用于验证用户统计功能"
            }
            await websocket.send(json.dumps(message))
            print("已发送文本消息")
            
            # 接收响应
            response = await websocket.recv()
            data = json.loads(response)
            print(f"收到响应: {data['type']}")
            
    except Exception as e:
        print(f"WebSocket测试失败: {e}")

def test_final_stats():
    """测试最终统计信息"""
    print("\n=== 最终用户统计 ===")
    
    headers = {"X-User-ID": USER_ID}
    response = requests.get(f"{BASE_URL}/api/v1/users/me/stats", headers=headers)
    if response.status_code == 200:
        stats = response.json()
        print(f"最终统计:")
        print(f"  - 总对话数: {stats['total_conversations']}")
        print(f"  - 总消息数: {stats['total_messages']}")
        print(f"  - 平均响应频率: {stats['avg_response_frequency']}")
        print(f"  - 最后活跃时间: {stats['last_active']}")
        print(f"  - 创建时间: {stats['created_at']}")

def main():
    """主函数"""
    print("开始PostgreSQL和用户功能测试...")
    
    # 测试数据库连接
    if not test_database_connection():
        print("数据库连接失败，退出测试")
        return
    
    # 测试用户API
    test_user_api()
    
    # 测试聊天功能
    test_chat_with_user_stats()
    
    # 测试WebSocket
    try:
        asyncio.run(test_websocket_with_user())
    except ImportError:
        print("WebSocket测试需要安装websockets库: pip install websockets")
    
    # 显示最终统计
    test_final_stats()
    
    print("\n✅ 所有测试完成!")

if __name__ == "__main__":
    main()
