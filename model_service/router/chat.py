from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger
import json

voice_router = APIRouter()


@voice_router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket连接已建立")
    try:
        while True:
            data = await websocket.receive_text()
            json_data = json.loads(data)
            logger.info(f"收到消息: {json_data}")
            if json_data["type"] == "audio":
                pass
        
            elif json_data["type"] == "wait":
                pass

            elif json_data["type"] == "text":
                pass
            
    except WebSocketDisconnect:
        logger.info("WebSocket连接已断开")
        await websocket.close()


