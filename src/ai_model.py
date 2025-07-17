"""
AI Model Manager for ChatGLM3 Discord Bot
"""

import os
from pathlib import Path
from typing import Optional, Tuple
import logging
from .config import ConfigManager

logger = logging.getLogger(__name__)


class AIModelManager:
    """Manages AI model operations"""

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """Initialize AI model manager"""
        self.config = config_manager or ConfigManager()
        self.model = None
        self.is_loaded = False
        self._load_model()

    def _load_model(self):
        """Load the ChatGLM3 model"""
        try:
            from gpt4all import GPT4All
            
            ai_config = self.config.get_ai_config()
            model_path = ai_config['model_path']
            
            if not os.path.exists(model_path):
                logger.error(f"Model file not found: {model_path}")
                return
            
            logger.info(f"Loading AI model from: {model_path}")
            self.model = GPT4All(model_path)
            self.is_loaded = True
            logger.info("AI model loaded successfully")
            
        except ImportError:
            logger.error("gpt4all package not installed")
        except Exception as e:
            logger.error(f"Failed to load AI model: {e}")

    def generate_sql(self, question: str) -> Tuple[Optional[str], Optional[str]]:
        """Generate SQL query from Chinese question"""
        if not self.is_loaded or not self.model:
            return None, "AI model not available"

        prompt = f"""Please convert the following Chinese question to MySQL SQL syntax. 
Return only the SQL query without any explanation:

Question: {question}
SQL:"""

        try:
            with self.model.chat_session():
                response = self.model.prompt(prompt).strip()
                # Clean up the response
                if response.startswith('```sql'):
                    response = response[6:]
                if response.endswith('```'):
                    response = response[:-3]
                response = response.strip()
                return response, None
        except Exception as e:
            logger.error(f"AI processing error: {e}")
            return None, f"AI processing error: {e}"

    def is_model_available(self) -> bool:
        """Check if model is available"""
        return self.is_loaded and self.model is not None 