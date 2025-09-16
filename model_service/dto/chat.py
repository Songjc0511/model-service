from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChatMessage(BaseModel):
    """聊天消息模型"""
    id: Optional[str] = None
    user_id: str
    conversation_id: str
    message_type: str  # "audio", "text", "wait"
    content: str
    timestamp: datetime
    is_user_message: bool = True

class Conversation(BaseModel):
    """对话模型"""
    id: str
    user_id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

class UserAuth(BaseModel):
    """用户认证信息"""
    user_id: str
    conversation_id: Optional[str] = None

class WebSocketMessage(BaseModel):
    """WebSocket消息模型"""
    type: str
    data: str
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
