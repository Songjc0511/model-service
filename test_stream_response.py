#!/usr/bin/env python3
"""
测试流式响应功能
"""
import asyncio
import websockets
import json

async def test_stream_response():
    """测试流式响应功能"""
    print("=== 测试流式响应功能 ===")
    
    # 测试不同的模型
    models_to_test = ["qwen-max", "qwen-plus", "qwen-turbo"]
    
    for model in models_to_test:
        print(f"\n测试模型: {model}")
        uri = f"ws://localhost:8000/api/v1/ws/chat?user_id=test_stream_user&model={model}"
        
        try:
            async with websockets.connect(uri) as websocket:
                print(f"✅ {model} WebSocket连接成功")
                
                # 等待服务器消息
                response = await websocket.recv()
                data = json.loads(response)
                print(f"收到服务器消息: {data}")
                
                # 发送测试消息
                test_message = {
                    "type": "text",
                    "data": "请写一首关于春天的短诗"
                }
                await websocket.send(json.dumps(test_message))
                print(f"已发送测试消息: {test_message['data']}")
                
                # 接收确认消息
                response = await websocket.recv()
                data = json.loads(response)
                print(f"收到确认: {data}")
                
                # 接收流式响应
                print(f"开始接收{model}的流式响应:")
                print("-" * 50)
                
                full_response = ""
                while True:
                    response = await websocket.recv()
                    data = json.loads(response)
                    
                    if data.get("type") == "model_stream":
                        chunk = data.get("text", "")
                        print(chunk, end="", flush=True)
                        full_response += chunk
                    elif data.get("type") == "model_stream_end":
                        print(f"\n{'-' * 50}")
                        print(f"✅ {model} 流式响应完成")
                        print(f"完整响应长度: {len(full_response)} 字符")
                        break
                    elif data.get("type") == "error":
                        print(f"❌ {model} 流式响应错误: {data.get('message')}")
                        break
                    else:
                        print(f"收到其他消息: {data}")
                
        except Exception as e:
            print(f"❌ {model} 测试失败: {e}")

async def test_long_response():
    """测试长文本流式响应"""
    print("\n=== 测试长文本流式响应 ===")
    
    uri = "ws://localhost:8000/api/v1/ws/chat?user_id=test_long_user&model=qwen-max"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket连接成功")
            
            # 等待服务器消息
            response = await websocket.recv()
            data = json.loads(response)
            print(f"收到服务器消息: {data}")
            
            # 发送长文本请求
            test_message = {
                "type": "text",
                "data": "请详细介绍一下人工智能的发展历史，包括重要的里程碑事件"
            }
            await websocket.send(json.dumps(test_message))
            print(f"已发送长文本请求")
            
            # 接收确认消息
            response = await websocket.recv()
            data = json.loads(response)
            print(f"收到确认: {data}")
            
            # 接收流式响应
            print("开始接收长文本流式响应:")
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
                    print(f"✅ 长文本流式响应完成")
                    print(f"总块数: {chunk_count}")
                    print(f"完整响应长度: {len(full_response)} 字符")
                    break
                elif data.get("type") == "error":
                    print(f"❌ 长文本流式响应错误: {data.get('message')}")
                    break
                else:
                    print(f"收到其他消息: {data}")
            
    except Exception as e:
        print(f"❌ 长文本测试失败: {e}")

def main():
    """主函数"""
    print("开始测试流式响应功能...")
    
    try:
        # 测试基本流式响应
        asyncio.run(test_stream_response())
        
        # 测试长文本流式响应
        asyncio.run(test_long_response())
        
    except Exception as e:
        print(f"测试失败: {e}")
    
    print("\n✅ 流式响应功能测试完成!")

if __name__ == "__main__":
    main()
