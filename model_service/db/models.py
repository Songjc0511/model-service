from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer
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
