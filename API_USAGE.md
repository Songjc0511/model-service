# API 使用说明

## 概述

本服务提供了基于用户ID和对话ID的聊天功能，支持音频转录、唤醒词检测和历史记录管理。

## 环境变量配置

在 `.env` 文件中设置以下环境变量：

```env
# 环境配置
ENV=dev

# 模型加载控制
LOAD_MODEL=true

# 数据库配置（可选）
DATABASE_URL=sqlite:///./chat_service.db
```

## WebSocket 连接

### 连接地址
```
ws://localhost:8000/api/v1/ws/chat?user_id={USER_ID}&conversation_id={CONVERSATION_ID}
```

### 参数说明
- `user_id` (必需): 用户唯一标识
- `conversation_id` (可选): 对话ID，如果不提供会自动创建新对话

### 消息格式

#### 发送消息
```json
{
    "type": "audio|text|wait",
    "data": "base64编码的音频数据或文本内容"
}
```

#### 接收消息
```json
{
    "type": "transcription|wake_word_detected|history|conversation_created|error",
    "text": "转录文本",
    "message": "状态消息",
    "conversation_id": "对话ID",
    "messages": [...]
}
```

## REST API 端点

### 聊天相关API

#### 1. 获取用户对话列表
```http
GET /api/v1/conversations
Headers:
  X-User-ID: {USER_ID}
```

#### 2. 获取对话消息历史
```http
GET /api/v1/conversations/{conversation_id}/messages
Headers:
  X-User-ID: {USER_ID}
```

#### 3. 创建新对话
```http
POST /api/v1/conversations?title={TITLE}
Headers:
  X-User-ID: {USER_ID}
```

#### 4. 关闭对话
```http
DELETE /api/v1/conversations/{conversation_id}
Headers:
  X-User-ID: {USER_ID}
```

### 用户管理API

#### 5. 创建用户
```http
POST /api/v1/users
Content-Type: application/json

{
    "id": "user123",
    "username": "用户名",
    "email": "user@example.com",
    "description": "用户描述",
    "response_frequency": 0.8,
    "preferences": {
        "language": "zh-CN",
        "theme": "dark"
    }
}
```

#### 6. 获取当前用户信息
```http
GET /api/v1/users/me
Headers:
  X-User-ID: {USER_ID}
```

#### 7. 更新当前用户信息
```http
PUT /api/v1/users/me
Headers:
  X-User-ID: {USER_ID}
Content-Type: application/json

{
    "username": "新用户名",
    "description": "新描述",
    "response_frequency": 0.9
}
```

#### 8. 获取用户统计信息
```http
GET /api/v1/users/me/stats
Headers:
  X-User-ID: {USER_ID}
```

#### 9. 搜索用户
```http
GET /api/v1/users/search?q={关键词}&limit=20
```

#### 10. 更新用户活跃时间
```http
POST /api/v1/users/me/activity
Headers:
  X-User-ID: {USER_ID}
```

#### 11. 健康检查
```http
GET /api/v1/health
```

## 使用示例

### JavaScript WebSocket 客户端

```javascript
// 连接WebSocket
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/chat?user_id=user123&conversation_id=conv456');

ws.onopen = function() {
    console.log('WebSocket连接已建立');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('收到消息:', data);
    
    switch(data.type) {
        case 'conversation_created':
            console.log('新对话ID:', data.conversation_id);
            break;
        case 'transcription':
            console.log('转录结果:', data.text);
            break;
        case 'wake_word_detected':
            console.log('检测到唤醒词:', data.text);
            break;
        case 'history':
            console.log('历史消息:', data.messages);
            break;
    }
};

// 发送音频数据
function sendAudio(audioBlob) {
    const reader = new FileReader();
    reader.onload = function() {
        const base64Data = reader.result.split(',')[1];
        ws.send(JSON.stringify({
            type: 'audio',
            data: base64Data
        }));
    };
    reader.readAsDataURL(audioBlob);
}

// 发送文本消息
function sendText(text) {
    ws.send(JSON.stringify({
        type: 'text',
        data: text
    }));
}
```

### Python 客户端示例

```python
import requests
import json

# 设置用户ID
USER_ID = "user123"
headers = {"X-User-ID": USER_ID}

# 用户管理示例
print("=== 用户管理 ===")

# 1. 创建用户
user_data = {
    "id": USER_ID,
    "username": "测试用户",
    "email": "test@example.com",
    "description": "这是一个测试用户",
    "response_frequency": 0.8,
    "preferences": {
        "language": "zh-CN",
        "theme": "dark"
    }
}
response = requests.post("http://localhost:8000/api/v1/users", json=user_data)
print("创建用户:", response.json())

# 2. 获取用户信息
response = requests.get("http://localhost:8000/api/v1/users/me", headers=headers)
user_info = response.json()
print("用户信息:", user_info)

# 3. 更新用户信息
update_data = {
    "description": "更新后的用户描述",
    "response_frequency": 0.9
}
response = requests.put("http://localhost:8000/api/v1/users/me", headers=headers, json=update_data)
print("更新用户:", response.json())

# 4. 获取用户统计
response = requests.get("http://localhost:8000/api/v1/users/me/stats", headers=headers)
stats = response.json()
print("用户统计:", stats)

# 聊天功能示例
print("\n=== 聊天功能 ===")

# 获取对话列表
response = requests.get(
    "http://localhost:8000/api/v1/conversations",
    headers=headers
)
conversations = response.json()
print("对话列表:", conversations)

# 创建新对话
response = requests.post(
    "http://localhost:8000/api/v1/conversations",
    headers=headers,
    params={"title": "新对话"}
)
new_conversation = response.json()
print("新对话:", new_conversation)

# 获取消息历史
conversation_id = new_conversation["conversation_id"]
response = requests.get(
    f"http://localhost:8000/api/v1/conversations/{conversation_id}/messages",
    headers=headers
)
messages = response.json()
print("消息历史:", messages)
```

## 功能特性

1. **用户验证**: 通过请求头中的 `X-User-ID` 进行用户身份验证
2. **用户管理**: 完整的用户CRUD操作，支持用户统计和偏好设置
3. **对话管理**: 支持创建、查询、关闭对话
4. **音频转录**: 使用 Whisper 模型进行音频转文字
5. **唤醒词检测**: 检测特定关键词触发对话
6. **历史记录**: 自动保存和查询对话历史
7. **用户统计**: 自动跟踪用户活跃度、对话数、消息数等统计信息
8. **PostgreSQL支持**: 使用PostgreSQL作为主数据库，支持向量搜索
9. **模型控制**: 通过环境变量控制是否加载模型
10. **自动用户创建**: 首次访问时自动创建用户账户

## 注意事项

1. 所有API请求都需要在请求头中包含 `X-User-ID`
2. WebSocket连接需要提供用户ID作为查询参数
3. 音频数据需要base64编码后发送
4. 数据库会自动创建，默认使用SQLite
5. 模型加载可以通过 `LOAD_MODEL` 环境变量控制
