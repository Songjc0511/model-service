import uvicorn
from dotenv import load_dotenv
from loguru import logger

from model_service.conf.env import settings

if __name__ == "__main__":
    load_dotenv()
    logger.info(f"current env: {settings.ENV}")
    port = 8000
    logger.info(f"Server will be available at: http://localhost:{port}")
    is_dev = settings.ENV == "dev"
    reload_excludes = ["tests", "tests/*", "tests/**/*"]
    uvicorn.run(
        "model_service.app:app",
        host="0.0.0.0",
        port=port,
        reload=is_dev,
        reload_excludes=reload_excludes,
        timeout_keep_alive=300,
        log_level="warning",  # 设置日志级别为 error
    )
