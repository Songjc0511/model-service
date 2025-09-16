#!/usr/bin/env python3
"""
测试模型回复功能
"""
import asyncio
import websockets
import json

async def test_model_response():
    """测试模型回复功能"""
    print("=== 测试模型回复功能 ===")
    
    # 测试不同的模型
    models_to_test = ["qwen-max", "qwen-plus", "qwen-turbo"]
    
    for model in models_to_test:
        print(f"\n测试模型: {model}")
        uri = f"ws://localhost:8000/api/v1/ws/chat?user_id=test_response_user&model={model}"
        
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
                    "data": "你好，请介绍一下你自己"
                }
                await websocket.send(json.dumps(test_message))
                print(f"已发送测试消息: {test_message['data']}")
                
                # 接收确认消息
                response = await websocket.recv()
                data = json.loads(response)
                print(f"收到确认: {data}")
                
                # 接收模型响应
                response = await websocket.recv()
                data = json.loads(response)
                print(f"模型响应: {data}")
                
                if data.get("type") == "model_response":
                    print(f"✅ {model} 模型回复成功: {data['text']}")
                else:
                    print(f"❌ {model} 模型回复失败: {data}")
                
        except Exception as e:
            print(f"❌ {model} 测试失败: {e}")

def main():
    """主函数"""
    print("开始测试模型回复功能...")
    
    try:
        asyncio.run(test_model_response())
    except Exception as e:
        print(f"测试失败: {e}")
    
    print("\n✅ 模型回复功能测试完成!")

if __name__ == "__main__":
    main()
