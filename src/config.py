"""Configuration settings for the Discord bot."""

import os
from typing import Optional

class Config:
    """Configuration class for the bot."""
    
    # Discord settings
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    
    # Database settings (optional - can be set via !connect command)
    DEFAULT_DB_HOST = os.getenv('DB_HOST')
    DEFAULT_DB_PORT = int(os.getenv('DB_PORT', '3306'))
    DEFAULT_DB_USER = os.getenv('DB_USER', 'root')
    DEFAULT_DB_PASSWORD = os.getenv('DB_PASSWORD', 'Meridian0723')
    DEFAULT_DB_NAME = os.getenv('DB_NAME', 'MyACG_data')
    
    # AI Model settings
    MODEL_PATH = os.getenv('MODEL_PATH', 'models/chatglm3-6b.Q4_K_M.gguf')
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '2048'))
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
    
    # Bot settings
    COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!')
    MAX_RESULTS = int(os.getenv('MAX_RESULTS', '50'))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        if not cls.DISCORD_TOKEN:
            print("❌ DISCORD_TOKEN environment variable is required")
            return False
        
        print("✅ Configuration validation passed")
        return True
    
    @classmethod
    def get_database_config(cls) -> dict:
        """Get database configuration."""
        return {
            'host': cls.DEFAULT_DB_HOST,
            'port': cls.DEFAULT_DB_PORT,
            'user': cls.DEFAULT_DB_USER,
            'password': cls.DEFAULT_DB_PASSWORD,
            'database': cls.DEFAULT_DB_NAME
        } 