from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from model_service.conf.settings import settings
from model_service.router.chat import voice_router
from model_service.router.user import user_router
from model_service.db.database import create_tables

# 创建FastAPI应用实例
app = FastAPI(
    title="Model Service",
    description="AI模型服务API - 支持用户验证和对话管理",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(voice_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    logger.info("应用启动中...")
    logger.info(f"当前环境: {settings.ENV}")
    logger.info(f"模型加载设置: {settings.LOAD_MODEL}")
    
    # 创建数据库表
    create_tables()
    logger.info("数据库表创建完成")
    
    if settings.LOAD_MODEL:
        logger.info("正在加载模型...")
        # 这里可以添加模型加载逻辑
        from model_service.service.audio.process_audio import load_model
        load_model()
        logger.info("模型加载完成")
    else:
        logger.info("跳过模型加载")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理"""
    logger.info("应用正在关闭...")

@app.get("/")
async def root():
    """根路径健康检查"""
    return {
        "message": "Model Service API",
        "version": "1.0.0",
        "env": settings.ENV,
        "model_loaded": settings.LOAD_MODEL,
        "features": [
            "用户验证",
            "对话管理", 
            "音频转录",
            "唤醒词检测",
            "历史记录查询"
        ]
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "env": settings.ENV,
        "model_loaded": settings.LOAD_MODEL
    }
