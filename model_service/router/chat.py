from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Request, Depends
from loguru import logger
import json
from model_service.service.audio.process_audio import transcribe, check_wake_word
from model_service.middleware.auth import auth_middleware
from model_service.service.chat_service import chat_service
from model_service.dto.chat import WebSocketMessage, Conversation, ChatMessage
from typing import List, Optional

voice_router = APIRouter()

# 存储活跃的WebSocket连接
active_connections = {}

@voice_router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    try:
        # 提取用户信息
        user_info = auth_middleware.extract_user_info_from_websocket(websocket)
        user_id = user_info["user_id"]
        conversation_id = user_info["conversation_id"]
        
        # 验证用户
        if not auth_middleware.validate_user(user_id):
            await websocket.close(code=1008, reason="用户验证失败")
            return
        
        # 获取或创建对话
        if not conversation_id:
            conversation_id = chat_service.get_or_create_conversation(user_id)
            # 发送新对话ID给客户端
            await websocket.send_text(json.dumps({
                "type": "conversation_created",
                "conversation_id": conversation_id
            }))
        else:
            conversation_id = chat_service.get_or_create_conversation(user_id, conversation_id)
        
        await websocket.accept()
        logger.info(f"WebSocket连接已建立 - 用户: {user_id}, 对话: {conversation_id}")
        
        # 存储连接信息
        active_connections[websocket] = {
            "user_id": user_id,
            "conversation_id": conversation_id
        }
        
        # 发送历史消息
        history = chat_service.get_conversation_messages(user_id, conversation_id, limit=10)
        if history:
            await websocket.send_text(json.dumps({
                "type": "history",
                "messages": [
                    {
                        "id": msg.id,
                        "type": msg.message_type,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat(),
                        "is_user": msg.is_user_message
                    }
                    for msg in history
                ]
            }))
        
        while True:
            data = await websocket.receive_text()
            json_data = json.loads(data)
            logger.info(f"收到消息: {json_data}")
            
            # 保存用户消息
            chat_service.save_message(
                user_id=user_id,
                conversation_id=conversation_id,
                message_type=json_data["type"],
                content=json_data.get("data", ""),
                is_user_message=True
            )
            
            if json_data["type"] == "audio":
                # 处理音频消息
                text = transcribe(json_data)
                if text:
                    # 检查唤醒词
                    if check_wake_word(text):
                        await websocket.send_text(json.dumps({
                            "type": "wake_word_detected",
                            "text": text,
                            "message": "检测到唤醒词，开始对话"
                        }))
                    else:
                        await websocket.send_text(json.dumps({
                            "type": "transcription",
                            "text": text
                        }))
                    
                    # 保存转录结果
                    chat_service.save_message(
                        user_id=user_id,
                        conversation_id=conversation_id,
                        message_type="transcription",
                        content=text,
                        is_user_message=False
                    )
                else:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "音频转录失败"
                    }))
        
            elif json_data["type"] == "wait":
                await websocket.send_text(json.dumps({
                    "type": "waiting",
                    "message": "等待中..."
                }))

            elif json_data["type"] == "text":
                text = json_data["data"]
                await websocket.send_text(json.dumps({
                    "type": "text_received",
                    "text": text
                }))
                
                # 保存文本消息
                chat_service.save_message(
                    user_id=user_id,
                    conversation_id=conversation_id,
                    message_type="text",
                    content=text,
                    is_user_message=False
                )
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket连接已断开 - 用户: {user_id}")
        if websocket in active_connections:
            del active_connections[websocket]
    except Exception as e:
        logger.error(f"WebSocket错误: {str(e)}")
        await websocket.close(code=1011, reason="服务器内部错误")


# REST API 端点
@voice_router.get("/conversations", response_model=List[Conversation])
async def get_user_conversations(request: Request, limit: int = 20):
    """获取用户的对话列表"""
    try:
        user_info = auth_middleware.extract_user_info_from_headers(request)
        user_id = user_info["user_id"]
        
        conversations = chat_service.get_user_conversations(user_id, limit)
        return conversations
    except Exception as e:
        logger.error(f"获取对话列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取对话列表失败")


@voice_router.get("/conversations/{conversation_id}/messages", response_model=List[ChatMessage])
async def get_conversation_messages(request: Request, conversation_id: str, limit: int = 50):
    """获取对话的消息历史"""
    try:
        user_info = auth_middleware.extract_user_info_from_headers(request)
        user_id = user_info["user_id"]
        
        messages = chat_service.get_conversation_messages(user_id, conversation_id, limit)
        return messages
    except Exception as e:
        logger.error(f"获取消息历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取消息历史失败")


@voice_router.post("/conversations", response_model=dict)
async def create_conversation(request: Request, title: Optional[str] = None):
    """创建新对话"""
    try:
        user_info = auth_middleware.extract_user_info_from_headers(request)
        user_id = user_info["user_id"]
        
        conversation_id = chat_service.create_conversation(user_id, title)
        return {
            "conversation_id": conversation_id,
            "message": "对话创建成功"
        }
    except Exception as e:
        logger.error(f"创建对话失败: {str(e)}")
        raise HTTPException(status_code=500, detail="创建对话失败")


@voice_router.delete("/conversations/{conversation_id}")
async def close_conversation(request: Request, conversation_id: str):
    """关闭对话"""
    try:
        user_info = auth_middleware.extract_user_info_from_headers(request)
        user_id = user_info["user_id"]
        
        success = chat_service.close_conversation(user_id, conversation_id)
        if success:
            return {"message": "对话已关闭"}
        else:
            raise HTTPException(status_code=404, detail="对话不存在或无权限")
    except Exception as e:
        logger.error(f"关闭对话失败: {str(e)}")
        raise HTTPException(status_code=500, detail="关闭对话失败")


@voice_router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "active_connections": len(active_connections)
    }
