from fastapi import APIRouter, HTTPException, Request, Query
from loguru import logger
from typing import List, Optional

from model_service.service.user_service import user_service
from model_service.dto.user import UserCreate, UserUpdate, UserResponse, UserStats
from model_service.middleware.auth import auth_middleware

user_router = APIRouter()

@user_router.post("/users", response_model=UserResponse)
async def create_user(user_data: UserCreate):
    """创建新用户"""
    try:
        user = user_service.create_user(user_data)
        logger.info(f"创建用户成功: {user.id}")
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建用户失败: {str(e)}")
        raise HTTPException(status_code=500, detail="创建用户失败")

@user_router.get("/users/me", response_model=UserResponse)
async def get_current_user(request: Request):
    """获取当前用户信息，如果不存在则自动创建"""
    try:
        user_info = auth_middleware.extract_user_info_from_headers(request)
        user_id = user_info["user_id"]
        
        # 验证用户是否存在，如果不存在则自动创建
        if not auth_middleware.validate_user(user_id):
            raise HTTPException(status_code=500, detail="用户验证失败")
        
        user = user_service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取用户信息失败")

@user_router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: str):
    """根据ID获取用户信息"""
    try:
        user = user_service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取用户信息失败")

@user_router.put("/users/me", response_model=UserResponse)
async def update_current_user(request: Request, user_data: UserUpdate):
    """更新当前用户信息"""
    try:
        user_info = auth_middleware.extract_user_info_from_headers(request)
        user_id = user_info["user_id"]
        
        # 验证用户是否存在，如果不存在则自动创建
        if not auth_middleware.validate_user(user_id):
            raise HTTPException(status_code=500, detail="用户验证失败")
        
        user = user_service.update_user(user_id, user_data)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        logger.info(f"更新用户成功: {user.id}")
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用户失败: {str(e)}")
        raise HTTPException(status_code=500, detail="更新用户失败")

@user_router.delete("/users/me")
async def delete_current_user(request: Request):
    """删除当前用户（软删除）"""
    try:
        user_info = auth_middleware.extract_user_info_from_headers(request)
        user_id = user_info["user_id"]
        
        success = user_service.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        logger.info(f"删除用户成功: {user_id}")
        return {"message": "用户已删除"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除用户失败: {str(e)}")
        raise HTTPException(status_code=500, detail="删除用户失败")

@user_router.get("/users/me/stats", response_model=UserStats)
async def get_current_user_stats(request: Request):
    """获取当前用户统计信息"""
    try:
        user_info = auth_middleware.extract_user_info_from_headers(request)
        user_id = user_info["user_id"]
        
        # 验证用户是否存在，如果不存在则自动创建
        if not auth_middleware.validate_user(user_id):
            raise HTTPException(status_code=500, detail="用户验证失败")
        
        stats = user_service.get_user_stats(user_id)
        if not stats:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取用户统计失败")

@user_router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    limit: int = Query(50, ge=1, le=100, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量")
):
    """获取所有用户列表（管理员功能）"""
    try:
        users = user_service.get_all_users(limit=limit, offset=offset)
        return users
    except Exception as e:
        logger.error(f"获取用户列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取用户列表失败")

@user_router.get("/users/search", response_model=List[UserResponse])
async def search_users(
    q: str = Query(..., description="搜索关键词"),
    limit: int = Query(20, ge=1, le=50, description="返回数量限制")
):
    """搜索用户"""
    try:
        users = user_service.search_users(q, limit=limit)
        return users
    except Exception as e:
        logger.error(f"搜索用户失败: {str(e)}")
        raise HTTPException(status_code=500, detail="搜索用户失败")

@user_router.post("/users/me/activity")
async def update_user_activity(request: Request):
    """更新用户活跃时间"""
    try:
        user_info = auth_middleware.extract_user_info_from_headers(request)
        user_id = user_info["user_id"]
        
        success = user_service.update_user_activity(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        return {"message": "活跃时间已更新"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用户活跃时间失败: {str(e)}")
        raise HTTPException(status_code=500, detail="更新用户活跃时间失败")
