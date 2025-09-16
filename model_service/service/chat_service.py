from sqlalchemy.orm import Session
from sqlalchemy import desc
from model_service.db.database import get_db_session
from model_service.db.models import Conversation, ChatMessage, User
from model_service.dto.chat import ChatMessage as ChatMessageDTO, Conversation as ConversationDTO
from model_service.service.user_service import user_service
from typing import List, Optional
from datetime import datetime
from uuid import uuid4
from loguru import logger

class ChatService:
    """聊天服务类"""
    
    def __init__(self):
        self.db = get_db_session()
    
    def create_conversation(self, user_id: str, title: Optional[str] = None) -> str:
        """创建新对话"""
        conversation_id = str(uuid4())
        conversation = Conversation(
            id=conversation_id,
            user_id=user_id,
            title=title or f"对话_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        self.db.add(conversation)
        self.db.commit()
        
        # 更新用户统计
        user_service.increment_user_stats(user_id, conversation_count=1)
        user_service.update_user_activity(user_id)
        
        logger.info(f"为用户 {user_id} 创建新对话: {conversation_id}")
        return conversation_id
    
    def get_user_conversations(self, user_id: str, limit: int = 20) -> List[ConversationDTO]:
        """获取用户的对话列表"""
        conversations = self.db.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.is_active == True
        ).order_by(desc(Conversation.updated_at)).limit(limit).all()
        
        return [
            ConversationDTO(
                id=conv.id,
                user_id=conv.user_id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                is_active=conv.is_active
            )
            for conv in conversations
        ]
    
    def get_conversation_messages(self, user_id: str, conversation_id: str, limit: int = 50) -> List[ChatMessageDTO]:
        """获取对话的消息历史"""
        messages = self.db.query(ChatMessage).filter(
            ChatMessage.user_id == user_id,
            ChatMessage.conversation_id == conversation_id
        ).order_by(ChatMessage.created_at).limit(limit).all()
        
        return [
            ChatMessageDTO(
                id=msg.id,
                user_id=msg.user_id,
                conversation_id=msg.conversation_id,
                message_type=msg.message_type,
                content=msg.content,
                timestamp=msg.created_at,
                is_user_message=msg.is_user_message
            )
            for msg in messages
        ]
    
    def save_message(self, user_id: str, conversation_id: str, message_type: str, 
                    content: str, is_user_message: bool = True) -> str:
        """保存消息到数据库"""
        message_id = str(uuid4())
        message = ChatMessage(
            id=message_id,
            user_id=user_id,
            conversation_id=conversation_id,
            message_type=message_type,
            content=content,
            is_user_message=is_user_message
        )
        
        self.db.add(message)
        
        # 更新对话的更新时间
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        if conversation:
            conversation.updated_at = datetime.now()
        
        self.db.commit()
        
        # 更新用户统计
        user_service.increment_user_stats(user_id, message_count=1)
        user_service.update_user_activity(user_id)
        
        logger.info(f"保存消息: {message_id} 到对话: {conversation_id}")
        return message_id
    
    def get_or_create_conversation(self, user_id: str, conversation_id: Optional[str] = None) -> str:
        """获取或创建对话"""
        if conversation_id:
            # 验证对话是否属于该用户
            conversation = self.db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
                Conversation.is_active == True
            ).first()
            
            if conversation:
                return conversation_id
            else:
                logger.warning(f"对话 {conversation_id} 不属于用户 {user_id} 或不存在")
        
        # 创建新对话
        return self.create_conversation(user_id)
    
    def close_conversation(self, user_id: str, conversation_id: str) -> bool:
        """关闭对话"""
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()
        
        if conversation:
            conversation.is_active = False
            self.db.commit()
            logger.info(f"关闭对话: {conversation_id}")
            return True
        
        return False

# 创建全局服务实例
chat_service = ChatService()
