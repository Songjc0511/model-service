from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from model_service.db.database import get_db_session
from model_service.db.models import User, Conversation, ChatMessage
from model_service.dto.user import UserCreate, UserUpdate, UserResponse, UserStats
from typing import List, Optional
from datetime import datetime
from loguru import logger

class UserService:
    """用户服务类"""
    
    def __init__(self):
        self.db = get_db_session()
    
    def create_user(self, user_data: UserCreate) -> UserResponse:
        """创建新用户"""
        # 检查用户是否已存在
        existing_user = self.db.query(User).filter(User.id == user_data.id).first()
        if existing_user:
            raise ValueError(f"用户 {user_data.id} 已存在")
        
        # 检查邮箱是否已存在
        if user_data.email:
            existing_email = self.db.query(User).filter(User.email == user_data.email).first()
            if existing_email:
                raise ValueError(f"邮箱 {user_data.email} 已被使用")
        
        # 创建新用户
        user = User(
            id=user_data.id,
            username=user_data.username,
            email=user_data.email,
            description=user_data.description,
            response_frequency=user_data.response_frequency,
            preferences=user_data.preferences or {}
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"创建用户: {user.id} - {user.username}")
        return self._user_to_response(user)
    
    def get_user(self, user_id: str) -> Optional[UserResponse]:
        """获取用户信息"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        return self._user_to_response(user)
    
    def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[UserResponse]:
        """更新用户信息"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # 检查邮箱是否被其他用户使用
        if user_data.email and user_data.email != user.email:
            existing_email = self.db.query(User).filter(
                User.email == user_data.email,
                User.id != user_id
            ).first()
            if existing_email:
                raise ValueError(f"邮箱 {user_data.email} 已被其他用户使用")
        
        # 更新字段
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"更新用户: {user.id}")
        return self._user_to_response(user)
    
    def delete_user(self, user_id: str) -> bool:
        """删除用户（软删除）"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        user.is_active = False
        user.updated_at = datetime.now()
        self.db.commit()
        
        logger.info(f"删除用户: {user.id}")
        return True
    
    def get_user_stats(self, user_id: str) -> Optional[UserStats]:
        """获取用户统计信息"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # 计算实际统计数据
        total_conversations = self.db.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.is_active == True
        ).count()
        
        total_messages = self.db.query(ChatMessage).filter(
            ChatMessage.user_id == user_id
        ).count()
        
        return UserStats(
            user_id=user.id,
            total_conversations=total_conversations,
            total_messages=total_messages,
            avg_response_frequency=user.response_frequency,
            last_active=user.last_active,
            created_at=user.created_at
        )
    
    def update_user_activity(self, user_id: str) -> bool:
        """更新用户活跃时间"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        user.last_active = datetime.now()
        self.db.commit()
        return True
    
    def increment_user_stats(self, user_id: str, conversation_count: int = 0, message_count: int = 0) -> bool:
        """增加用户统计计数"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        user.total_conversations += conversation_count
        user.total_messages += message_count
        user.last_active = datetime.now()
        user.updated_at = datetime.now()
        
        self.db.commit()
        return True
    
    def get_all_users(self, limit: int = 50, offset: int = 0) -> List[UserResponse]:
        """获取所有用户列表"""
        users = self.db.query(User).filter(User.is_active == True).offset(offset).limit(limit).all()
        return [self._user_to_response(user) for user in users]
    
    def search_users(self, query: str, limit: int = 20) -> List[UserResponse]:
        """搜索用户"""
        users = self.db.query(User).filter(
            User.is_active == True,
            (User.username.ilike(f"%{query}%") | 
             User.email.ilike(f"%{query}%") |
             User.description.ilike(f"%{query}%"))
        ).limit(limit).all()
        
        return [self._user_to_response(user) for user in users]
    
    def _user_to_response(self, user: User) -> UserResponse:
        """将User模型转换为UserResponse"""
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            description=user.description,
            response_frequency=user.response_frequency,
            preferences=user.preferences,
            total_conversations=user.total_conversations,
            total_messages=user.total_messages,
            last_active=user.last_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            is_active=user.is_active
        )

# 创建全局服务实例
user_service = UserService()
