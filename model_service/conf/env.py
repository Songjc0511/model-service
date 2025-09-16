"""
Legacy configuration settings for backward compatibility.

This module provides the original Settings class for backward compatibility
while delegating to the new structured configuration system.
"""

from model_service.conf.settings import settings

# For backward compatibility, we expose the new settings instance
# under the old name and structure
Settings = settings.__class__

# 导出settings实例供其他模块使用
__all__ = ['settings', 'Settings']