from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from model_service.conf.settings import settings
from model_service.db.models import Base
import os

# 数据库URL配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chat_service.db")

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    poolclass=StaticPool if "sqlite" in DATABASE_URL else None,
    echo=False
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """创建数据库表"""
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session() -> Session:
    """获取数据库会话（非依赖注入方式）"""
    return SessionLocal()
