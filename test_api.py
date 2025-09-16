#!/usr/bin/env python3
"""
API功能测试脚本
"""
import requests
import json
import asyncio
import websockets
from datetime import datetime

# 测试配置
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/api/v1/ws/chat"
USER_ID = "test_user_123"
CONVERSATION_ID = None

def test_rest_api():
    """测试REST API"""
    print("=== 测试REST API ===")
    
    headers = {"X-User-ID": USER_ID}
    
    # 1. 健康检查
    print("1. 健康检查...")
    response = requests.get(f"{BASE_URL}/api/v1/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    # 2. 创建对话
    print("\n2. 创建对话...")
    response = requests.post(
        f"{BASE_URL}/api/v1/conversations",
        headers=headers,
        params={"title": f"测试对话_{datetime.now().strftime('%H%M%S')}"}
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        conversation_data = response.json()
        global CONVERSATION_ID
        CONVERSATION_ID = conversation_data["conversation_id"]
        print(f"对话ID: {CONVERSATION_ID}")
    
    # 3. 获取对话列表
    print("\n3. 获取对话列表...")
    response = requests.get(f"{BASE_URL}/api/v1/conversations", headers=headers)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        conversations = response.json()
        print(f"对话数量: {len(conversations)}")
        for conv in conversations[:3]:  # 只显示前3个
            print(f"  - {conv['id']}: {conv['title']}")
    
    # 4. 获取消息历史
    if CONVERSATION_ID:
        print(f"\n4. 获取对话 {CONVERSATION_ID} 的消息历史...")
        response = requests.get(
            f"{BASE_URL}/api/v1/conversations/{CONVERSATION_ID}/messages",
            headers=headers
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            messages = response.json()
            print(f"消息数量: {len(messages)}")

async def test_websocket():
    """测试WebSocket连接"""
    print("\n=== 测试WebSocket ===")
    
    uri = f"{WS_URL}?user_id={USER_ID}"
    if CONVERSATION_ID:
        uri += f"&conversation_id={CONVERSATION_ID}"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("WebSocket连接已建立")
            
            # 发送文本消息
            message = {
                "type": "text",
                "data": "这是一条测试消息"
            }
            await websocket.send(json.dumps(message))
            print("已发送文本消息")
            
            # 接收响应
            response = await websocket.recv()
            data = json.loads(response)
            print(f"收到响应: {data}")
            
            # 发送等待消息
            wait_message = {
                "type": "wait",
                "data": ""
            }
            await websocket.send(json.dumps(wait_message))
            print("已发送等待消息")
            
            # 接收响应
            response = await websocket.recv()
            data = json.loads(response)
            print(f"收到响应: {data}")
            
    except Exception as e:
        print(f"WebSocket测试失败: {e}")

def main():
    """主函数"""
    print("开始API功能测试...")
    
    # 测试REST API
    test_rest_api()
    
    # 测试WebSocket
    try:
        asyncio.run(test_websocket())
    except ImportError:
        print("WebSocket测试需要安装websockets库: pip install websockets")
    
    print("\n测试完成!")

if __name__ == "__main__":
    main()
