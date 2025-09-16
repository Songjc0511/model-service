#!/usr/bin/env python3
"""
WebSocket连接测试脚本
"""
import asyncio
import websockets
import json

async def test_websocket_connection():
    """测试WebSocket连接"""
    print("=== WebSocket连接测试 ===")
    
    # WebSocket URL
    uri = "ws://localhost:8000/api/v1/ws/chat?user_id=test_ws_user&conversation_id=test_conv_123"
    
    try:
        print(f"正在连接到: {uri}")
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket连接成功!")
            
            # 等待服务器发送的初始消息
            print("等待服务器消息...")
            response = await websocket.recv()
            data = json.loads(response)
            print(f"收到服务器消息: {data}")
            
            # 发送测试消息
            test_message = {
                "type": "text",
                "data": "这是一条测试消息"
            }
            await websocket.send(json.dumps(test_message))
            print("已发送测试消息")
            
            # 接收响应
            response = await websocket.recv()
            data = json.loads(response)
            print(f"收到响应: {data}")
            
            # 发送音频消息（模拟）
            audio_message = {
                "type": "audio",
                "data": "base64_encoded_audio_data_here"
            }
            await websocket.send(json.dumps(audio_message))
            print("已发送音频消息")
            
            # 接收响应
            response = await websocket.recv()
            data = json.loads(response)
            print(f"收到音频响应: {data}")
            
            print("✅ WebSocket测试完成!")
            
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ WebSocket连接被关闭: {e}")
    except Exception as e:
        print(f"❌ WebSocket连接失败: {e}")

async def test_websocket_without_conversation():
    """测试不带conversation_id的WebSocket连接"""
    print("\n=== 测试自动创建对话 ===")
    
    uri = "ws://localhost:8000/api/v1/ws/chat?user_id=test_auto_user"
    
    try:
        print(f"正在连接到: {uri}")
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket连接成功!")
            
            # 等待服务器发送的初始消息
            print("等待服务器消息...")
            response = await websocket.recv()
            data = json.loads(response)
            print(f"收到服务器消息: {data}")
            
            if data.get("type") == "conversation_created":
                print(f"✅ 自动创建对话成功: {data['conversation_id']}")
            
            print("✅ 自动创建对话测试完成!")
            
    except Exception as e:
        print(f"❌ 自动创建对话测试失败: {e}")

def main():
    """主函数"""
    print("开始WebSocket连接测试...")
    
    try:
        # 测试基本连接
        asyncio.run(test_websocket_connection())
        
        # 测试自动创建对话
        asyncio.run(test_websocket_without_conversation())
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"测试过程中出错: {e}")

if __name__ == "__main__":
    main()
