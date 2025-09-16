from fastapi import Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from loguru import logger
import json

class UserAuthMiddleware:
    """用户认证中间件"""
    
    def __init__(self):
        self.security = HTTPBearer(auto_error=False)
    
    def extract_user_info_from_headers(self, request: Request) -> dict:
        """从请求头中提取用户信息"""
        user_id = request.headers.get("X-User-ID")
        conversation_id = request.headers.get("X-Conversation-ID")
        model = request.headers.get("X-Model", "qwen-max")  # 默认使用qwen-max
        
        if not user_id:
            raise HTTPException(
                status_code=401, 
                detail="缺少用户ID，请在请求头中添加 X-User-ID"
            )
        
        return {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "model": model
        }
    
    def extract_user_info_from_websocket(self, websocket: WebSocket) -> dict:
        """从WebSocket连接中提取用户信息"""
        # 从查询参数获取用户信息
        user_id = websocket.query_params.get("user_id")
        conversation_id = websocket.query_params.get("conversation_id")
        model = websocket.query_params.get("model", "qwen-max")  # 默认使用qwen-max
        
        if not user_id:
            raise WebSocketDisconnect(code=1008, reason="缺少用户ID参数")
        
        return {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "model": model
        }
    
    def validate_user(self, user_id: str) -> bool:
        """验证用户是否存在，如果不存在则自动创建"""
        from model_service.service.user_service import user_service
        
        # 检查用户是否存在
        user = user_service.get_user(user_id)
        if user:
            return True
        
        # 如果用户不存在，自动创建
        try:
            from model_service.dto.user import UserCreate
            user_data = UserCreate(
                id=user_id,
                username=f"user_{user_id}",
                description=f"自动创建的用户 {user_id}",
                response_frequency=1.0
            )
            user_service.create_user(user_data)
            logger.info(f"自动创建用户: {user_id}")
            return True
        except Exception as e:
            logger.error(f"自动创建用户失败: {e}")
            return False

# 创建全局中间件实例
auth_middleware = UserAuthMiddleware()
