#!/usr/bin/env python3
"""
模型功能测试脚本
"""
import requests
import json
import asyncio
import websockets

def test_model_api():
    """测试模型API"""
    print("=== 测试模型API ===")
    
    # 1. 获取可用模型列表
    print("1. 获取可用模型列表...")
    response = requests.get("http://localhost:8000/api/v1/models")
    if response.status_code == 200:
        models_data = response.json()
        print(f"可用模型数量: {models_data['total_count']}")
        print("可用模型:")
        for model_name, model_info in models_data['models'].items():
            print(f"  - {model_name}: {model_info['name']} ({model_info['description']})")
    else:
        print(f"❌ 获取模型列表失败: {response.status_code}")
    
    # 2. 获取特定模型信息
    print("\n2. 获取qwen-max模型信息...")
    response = requests.get("http://localhost:8000/api/v1/models/qwen-max")
    if response.status_code == 200:
        model_data = response.json()
        print(f"模型: {model_data['model']}")
        print(f"信息: {model_data['info']}")
    else:
        print(f"❌ 获取模型信息失败: {response.status_code}")
    
    # 3. 测试不存在的模型
    print("\n3. 测试不存在的模型...")
    response = requests.get("http://localhost:8000/api/v1/models/nonexistent-model")
    if response.status_code == 404:
        print("✅ 正确处理了不存在的模型")
    else:
        print(f"❌ 预期404，实际: {response.status_code}")

async def test_websocket_with_models():
    """测试WebSocket与不同模型"""
    print("\n=== 测试WebSocket模型功能 ===")
    
    # 测试不同的模型
    models_to_test = ["qwen-max", "qwen-plus", "qwen-turbo", "gpt-4"]
    
    for model in models_to_test:
        print(f"\n测试模型: {model}")
        uri = f"ws://localhost:8000/api/v1/ws/chat?user_id=test_model_user&model={model}"
        
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
                    "data": f"你好，这是测试{model}模型的消息"
                }
                await websocket.send(json.dumps(test_message))
                print(f"已发送测试消息到{model}")
                
                # 接收响应
                response = await websocket.recv()
                data = json.loads(response)
                print(f"收到确认: {data}")
                
                # 接收模型响应
                response = await websocket.recv()
                data = json.loads(response)
                print(f"模型响应: {data}")
                
        except Exception as e:
            print(f"❌ {model} 测试失败: {e}")

def test_health_with_models():
    """测试健康检查包含模型信息"""
    print("\n=== 测试健康检查 ===")
    
    response = requests.get("http://localhost:8000/api/v1/health")
    if response.status_code == 200:
        health_data = response.json()
        print(f"服务状态: {health_data['status']}")
        print(f"活跃连接数: {health_data['active_connections']}")
        print(f"可用模型数: {health_data['available_models']}")
    else:
        print(f"❌ 健康检查失败: {response.status_code}")

def main():
    """主函数"""
    print("开始模型功能测试...")
    
    # 测试REST API
    test_model_api()
    
    # 测试健康检查
    test_health_with_models()
    
    # 测试WebSocket
    try:
        asyncio.run(test_websocket_with_models())
    except Exception as e:
        print(f"WebSocket测试失败: {e}")
    
    print("\n✅ 模型功能测试完成!")

if __name__ == "__main__":
    main()
