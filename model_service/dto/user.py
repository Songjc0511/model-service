from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class UserCreate(BaseModel):
    """创建用户请求模型"""
    id: str = Field(..., description="用户唯一标识")
    username: str = Field(..., description="用户名")
    email: Optional[str] = Field(None, description="邮箱")
    description: Optional[str] = Field(None, description="用户描述")
    response_frequency: float = Field(1.0, ge=0.0, le=1.0, description="响应频率")
    preferences: Optional[Dict[str, Any]] = Field(None, description="用户偏好设置")

class UserUpdate(BaseModel):
    """更新用户请求模型"""
    username: Optional[str] = Field(None, description="用户名")
    email: Optional[str] = Field(None, description="邮箱")
    description: Optional[str] = Field(None, description="用户描述")
    response_frequency: Optional[float] = Field(None, ge=0.0, le=1.0, description="响应频率")
    preferences: Optional[Dict[str, Any]] = Field(None, description="用户偏好设置")

class UserResponse(BaseModel):
    """用户响应模型"""
    id: str
    username: str
    email: Optional[str]
    description: Optional[str]
    response_frequency: float
    preferences: Optional[Dict[str, Any]]
    total_conversations: int
    total_messages: int
    last_active: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    is_active: bool

class UserStats(BaseModel):
    """用户统计信息模型"""
    user_id: str
    total_conversations: int
    total_messages: int
    avg_response_frequency: float
    last_active: Optional[datetime]
    created_at: datetime
