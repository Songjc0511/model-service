from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(String(50), primary_key=True)
    username = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    description = Column(Text, nullable=True)  # 用户描述
    response_frequency = Column(Float, default=1.0)  # 响应频率（0.0-1.0）
    preferences = Column(JSON, nullable=True)  # 用户偏好设置
    total_conversations = Column(Integer, default=0)  # 总对话数
    total_messages = Column(Integer, default=0)  # 总消息数
    last_active = Column(DateTime, nullable=True)  # 最后活跃时间
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)

class Conversation(Base):
    """对话表"""
    __tablename__ = "conversations"
    
    id = Column(String(50), primary_key=True)
    user_id = Column(String(50), nullable=False, index=True)
    title = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)

class ChatMessage(Base):
    """聊天消息表"""
    __tablename__ = "chat_messages"
    
    id = Column(String(50), primary_key=True)
    user_id = Column(String(50), nullable=False, index=True)
    conversation_id = Column(String(50), nullable=False, index=True)
    message_type = Column(String(20), nullable=False)  # "audio", "text", "wait"
    content = Column(Text, nullable=False)
    is_user_message = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
