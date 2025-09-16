from typing import Dict, Any, Optional
from loguru import logger
import asyncio

class ModelService:
    """模型管理服务"""
    
    def __init__(self):
        # 支持的模型列表
        self.supported_models = {
            "qwen-max": {
                "name": "通义千问-Max",
                "provider": "qwen-api",
                "description": "阿里云通义千问最大模型",
                "enabled": True
            },
            "qwen-plus": {
                "name": "通义千问-Plus", 
                "provider": "qwen-api",
                "description": "阿里云通义千问增强模型",
                "enabled": True
            },
            "qwen-turbo": {
                "name": "通义千问-Turbo",
                "provider": "qwen-api", 
                "description": "阿里云通义千问快速模型",
                "enabled": True
            },
            "gpt-4": {
                "name": "GPT-4",
                "provider": "openai",
                "description": "OpenAI GPT-4模型",
                "enabled": False  # 暂时禁用
            },
            "gpt-3.5-turbo": {
                "name": "GPT-3.5 Turbo",
                "provider": "openai", 
                "description": "OpenAI GPT-3.5 Turbo模型",
                "enabled": False  # 暂时禁用
            },
            "claude-3": {
                "name": "Claude-3",
                "provider": "anthropic",
                "description": "Anthropic Claude-3模型", 
                "enabled": False  # 暂时禁用
            }
        }
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """获取模型信息"""
        return self.supported_models.get(model_name)
    
    def is_model_supported(self, model_name: str) -> bool:
        """检查模型是否支持"""
        model_info = self.get_model_info(model_name)
        return model_info is not None and model_info.get("enabled", False)
    
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """获取所有可用的模型"""
        return {name: info for name, info in self.supported_models.items() if info.get("enabled", False)}
    
    def process_chat_request(self, model_name: str, messages: list, **kwargs) -> str:
        """处理聊天请求"""
        if not self.is_model_supported(model_name):
            logger.warning(f"不支持的模型: {model_name}")
            return "抱歉，当前模型暂不支持，请选择其他模型。"
        
        model_info = self.get_model_info(model_name)
        provider = model_info.get("provider")
        
        if provider == "qwen-api":
            return self._process_qwen_request(model_name, messages, **kwargs)
        elif provider == "openai":
            return self._process_openai_request(model_name, messages, **kwargs)
        elif provider == "anthropic":
            return self._process_claude_request(model_name, messages, **kwargs)
        else:
            logger.error(f"未知的模型提供商: {provider}")
            return "抱歉，模型提供商暂不支持。"
    
    async def process_chat_stream(self, model_name: str, messages: list, **kwargs):
        """处理流式聊天请求"""
        if not self.is_model_supported(model_name):
            logger.warning(f"不支持的模型: {model_name}")
            yield "抱歉，当前模型暂不支持，请选择其他模型。"
            return
        
        model_info = self.get_model_info(model_name)
        provider = model_info.get("provider")
        
        if provider == "qwen-api":
            async for chunk in self._process_qwen_stream(model_name, messages, **kwargs):
                yield chunk
        elif provider == "openai":
            async for chunk in self._process_openai_stream(model_name, messages, **kwargs):
                yield chunk
        elif provider == "anthropic":
            async for chunk in self._process_claude_stream(model_name, messages, **kwargs):
                yield chunk
        else:
            logger.error(f"未知的模型提供商: {provider}")
            yield "抱歉，模型提供商暂不支持。"
    
    def _process_qwen_request(self, model_name: str, messages: list, **kwargs) -> str:
        """处理通义千问请求"""
        try:
            from model_service.models.chat.chat import chat
            logger.info(f"使用通义千问模型: {model_name}")
            
            # 实际调用通义千问模型
            response = chat(messages)
            logger.info(f"通义千问模型响应: {response}")
            return response
            
        except Exception as e:
            logger.error(f"通义千问模型调用失败: {e}")
            return "抱歉，模型调用失败，请稍后重试。"
    
    async def _process_qwen_stream(self, model_name: str, messages: list, **kwargs):
        """处理通义千问流式请求"""
        try:
            from model_service.models.chat.chat import chat_stream
            logger.info(f"使用通义千问流式模型: {model_name}")
            
            # 调用流式模型（同步生成器转换为异步）
            for chunk in chat_stream(messages):
                yield chunk
                # 添加小延迟以模拟异步行为
                await asyncio.sleep(0.01)
                
        except Exception as e:
            logger.error(f"通义千问流式模型调用失败: {e}")
            yield "抱歉，模型调用失败，请稍后重试。"
    
    def _process_openai_request(self, model_name: str, messages: list, **kwargs) -> str:
        """处理OpenAI请求"""
        logger.info(f"使用OpenAI模型: {model_name}")
        # 暂时返回pass
        return "pass"
    
    async def _process_openai_stream(self, model_name: str, messages: list, **kwargs):
        """处理OpenAI流式请求"""
        logger.info(f"使用OpenAI流式模型: {model_name}")
        # 暂时返回pass
        yield "pass"
    
    def _process_claude_request(self, model_name: str, messages: list, **kwargs) -> str:
        """处理Claude请求"""
        logger.info(f"使用Claude模型: {model_name}")
        # 暂时返回pass
        return "pass"
    
    async def _process_claude_stream(self, model_name: str, messages: list, **kwargs):
        """处理Claude流式请求"""
        logger.info(f"使用Claude流式模型: {model_name}")
        # 暂时返回pass
        yield "pass"
    
    def get_model_list_response(self) -> Dict[str, Any]:
        """获取模型列表响应"""
        available_models = self.get_available_models()
        return {
            "models": available_models,
            "default_model": "qwen-max",
            "total_count": len(available_models)
        }

# 创建全局模型服务实例
model_service = ModelService()
