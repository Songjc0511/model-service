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
        
        if not user_id:
            raise HTTPException(
                status_code=401, 
                detail="缺少用户ID，请在请求头中添加 X-User-ID"
            )
        
        return {
            "user_id": user_id,
            "conversation_id": conversation_id
        }
    
    def extract_user_info_from_websocket(self, websocket: WebSocket) -> dict:
        """从WebSocket连接中提取用户信息"""
        # 从查询参数获取用户信息
        user_id = websocket.query_params.get("user_id")
        conversation_id = websocket.query_params.get("conversation_id")
        
        if not user_id:
            raise WebSocketDisconnect(code=1008, reason="缺少用户ID参数")
        
        return {
            "user_id": user_id,
            "conversation_id": conversation_id
        }
    
    def validate_user(self, user_id: str) -> bool:
        """验证用户是否存在（这里可以添加实际的用户验证逻辑）"""
        # 这里可以添加数据库查询或其他验证逻辑
        # 目前简单返回True
        return True

# 创建全局中间件实例
auth_middleware = UserAuthMiddleware()
