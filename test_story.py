#!/usr/bin/env python3
"""
测试故事生成功能
"""
import asyncio
import websockets
import json

async def test_story_generation():
    """测试故事生成功能"""
    print("=== 测试故事生成功能 ===")
    
    uri = "ws://localhost:8000/api/v1/ws/chat?user_id=test_story_user&model=qwen-max"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket连接成功")
            
            # 等待服务器消息
            response = await websocket.recv()
            data = json.loads(response)
            print(f"收到服务器消息: {data}")
            
            # 发送故事请求
            test_message = {
                "type": "text",
                "data": "给我讲个二百字的故事"
            }
            await websocket.send(json.dumps(test_message))
            print(f"已发送测试消息: {test_message['data']}")
            
            # 接收确认消息
            response = await websocket.recv()
            data = json.loads(response)
            print(f"收到确认: {data}")
            
            # 接收流式响应
            print("开始接收故事:")
            print("=" * 60)
            
            full_response = ""
            chunk_count = 0
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                
                if data.get("type") == "model_stream":
                    chunk = data.get("text", "")
                    print(chunk, end="", flush=True)
                    full_response += chunk
                    chunk_count += 1
                elif data.get("type") == "model_stream_end":
                    print(f"\n{'=' * 60}")
                    print(f"✅ 故事生成完成")
                    print(f"总块数: {chunk_count}")
                    print(f"故事长度: {len(full_response)} 字符")
                    break
                elif data.get("type") == "error":
                    print(f"❌ 故事生成错误: {data.get('message')}")
                    break
                else:
                    print(f"收到其他消息: {data}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

async def test_conversation_context():
    """测试对话上下文"""
    print("\n=== 测试对话上下文 ===")
    
    uri = "ws://localhost:8000/api/v1/ws/chat?user_id=test_context_user&model=qwen-max"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket连接成功")
            
            # 等待服务器消息
            response = await websocket.recv()
            data = json.loads(response)
            print(f"收到服务器消息: {data}")
            
            # 第一轮对话
            print("\n第一轮对话:")
            message1 = {
                "type": "text",
                "data": "我叫小明"
            }
            await websocket.send(json.dumps(message1))
            print(f"发送: {message1['data']}")
            
            # 接收第一轮响应
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                if data.get("type") == "text_received":
                    print(f"确认: {data}")
                    break
            
            # 接收第一轮模型响应
            print("第一轮回复:")
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                if data.get("type") == "model_stream":
                    print(data.get("text", ""), end="", flush=True)
                elif data.get("type") == "model_stream_end":
                    print("\n第一轮对话结束\n")
                    break
            
            # 第二轮对话
            print("第二轮对话:")
            message2 = {
                "type": "text",
                "data": "我刚才说我叫什么名字？"
            }
            await websocket.send(json.dumps(message2))
            print(f"发送: {message2['data']}")
            
            # 接收第二轮响应
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                if data.get("type") == "text_received":
                    print(f"确认: {data}")
                    break
            
            # 接收第二轮模型响应
            print("第二轮回复:")
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                if data.get("type") == "model_stream":
                    print(data.get("text", ""), end="", flush=True)
                elif data.get("type") == "model_stream_end":
                    print("\n第二轮对话结束")
                    break
            
    except Exception as e:
        print(f"❌ 上下文测试失败: {e}")

def main():
    """主函数"""
    print("开始测试故事生成和对话上下文...")
    
    try:
        # 测试故事生成
        asyncio.run(test_story_generation())
        
        # 测试对话上下文
        asyncio.run(test_conversation_context())
        
    except Exception as e:
        print(f"测试失败: {e}")
    
    print("\n✅ 测试完成!")

if __name__ == "__main__":
    main()
