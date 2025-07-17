"""
Configuration Manager for ChatGLM3 Discord Bot
"""

import os
from pathlib import Path
from typing import Optional, Any
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages application configuration"""

    def __init__(self, env_file: Optional[str] = None):
        """Initialize configuration manager"""
        self._config = {}
        self._load_environment(env_file)

    def _load_environment(self, env_file: Optional[str] = None):
        """Load environment variables"""
        if env_file:
            load_dotenv(env_file)
        else:
            # Try to find .env file in project root
            env_path = Path(__file__).parent.parent / '.env'
            if env_path.exists():
                load_dotenv(env_path)
            else:
                logger.warning("No .env file found, using system environment variables")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return os.getenv(key, default)

    def get_required(self, key: str) -> str:
        """Get required configuration value"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required configuration '{key}' not found")
        return value

    def validate_required_keys(self) -> tuple[bool, list[str]]:
        """Validate all required configuration keys are present"""
        required_keys = [
            'DISCORD_TOKEN',
            'MYSQL_HOST',
            'MYSQL_USER',
            'MYSQL_PASSWORD',
            'MYSQL_DATABASE',
            'MODEL_PATH'
        ]
        
        missing_keys = []
        for key in required_keys:
            if not os.getenv(key):
                missing_keys.append(key)
        
        return len(missing_keys) == 0, missing_keys

    def get_database_config(self) -> dict:
        """Get database configuration"""
        return {
            'host': self.get_required('MYSQL_HOST'),
            'user': self.get_required('MYSQL_USER'),
            'password': self.get_required('MYSQL_PASSWORD'),
            'database': self.get_required('MYSQL_DATABASE'),
            'port': int(self.get('MYSQL_PORT', 3306))
        }

    def get_ai_config(self) -> dict:
        """Get AI model configuration"""
        return {
            'model_path': self.get_required('MODEL_PATH'),
            'threads': int(self.get('AI_THREADS', 0)),
            'memory_limit': int(self.get('AI_MEMORY_LIMIT', 0))
        }

    def get_bot_config(self) -> dict:
        """Get bot configuration"""
        return {
            'token': self.get_required('DISCORD_TOKEN'),
            'command_prefix': self.get('COMMAND_PREFIX', '!'),
            'max_results': int(self.get('MAX_RESULTS', 100)),
            'log_level': self.get('LOG_LEVEL', 'INFO')
        } 