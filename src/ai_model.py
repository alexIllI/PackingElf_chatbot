"""
AI Model Manager for ChatGLM3 Discord Bot
"""

import os
from pathlib import Path
from typing import Optional, Tuple
import logging
from config import Config

logger = logging.getLogger(__name__)


class AIModelManager:
    """Manages AI model operations"""

    def __init__(self, config: Optional[Config] = None):
        """Initialize AI model manager"""
        self.config = config or Config
        self.model = None
        self.is_loaded = False
        self._load_model()

    def _load_model(self):
        """Load the ChatGLM3 model"""
        try:
            from llama_cpp import Llama
            
            model_path = self.config.MODEL_PATH
            
            if not os.path.exists(model_path):
                logger.error(f"Model file not found: {model_path}")
                return
            
            logger.info(f"Loading AI model from: {model_path}")
            
            # Initialize Llama model with ChatGLM3 settings
            self.model = Llama(
                model_path=model_path,
                n_ctx=2048,  # Context window
                n_threads=4,  # Number of CPU threads
                n_gpu_layers=0,  # No GPU layers for CPU-only
                verbose=False
            )
            
            self.is_loaded = True
            logger.info("AI model loaded successfully")
            
        except ImportError:
            logger.error("llama-cpp-python package not installed. Install with: pip install llama-cpp-python")
        except Exception as e:
            logger.error(f"Failed to load AI model: {e}")

    def generate_sql(self, question: str) -> Tuple[Optional[str], Optional[str]]:
        """Generate SQL query from Chinese question"""
        if not self.is_loaded or not self.model:
            return None, "AI model not available"

        prompt = f"""<|im_start|>system
You are a helpful assistant that converts Chinese questions to MySQL SQL queries. Return only the SQL query without any explanation.
<|im_end|>
<|im_start|>user
{question}
<|im_end|>
<|im_start|>assistant
"""

        try:
            response = self.model(
                prompt,
                max_tokens=512,
                temperature=0.1,
                stop=["<|im_end|>"]
            )
            
            # Handle response format properly
            if isinstance(response, dict) and 'choices' in response:
                sql_query = response['choices'][0]['text'].strip()
            else:
                return None, "Invalid response format"
            
            # Clean up the response
            if sql_query.startswith('```sql'):
                sql_query = sql_query[6:]
            if sql_query.endswith('```'):
                sql_query = sql_query[:-3]
            sql_query = sql_query.strip()
            
            return sql_query, None
            
        except Exception as e:
            logger.error(f"AI processing error: {e}")
            return None, f"AI processing error: {e}"

    def is_model_available(self) -> bool:
        """Check if model is available"""
        return self.is_loaded and self.model is not None
    
    async def process_query(self, question: str) -> Optional[str]:
        """Process a query using AI and return a response"""
        if not self.is_loaded or not self.model:
            return None

        prompt = f"""<|im_start|>system
你是一個資料庫查詢助手。根據用戶的問題，提供簡潔的繁體中文回答。如果問題涉及訂單查詢但找不到結果，請提供有用的建議。

請注意：
1. 如果用戶查詢訂單號，請確認格式是否正確
2. 如果找不到結果，請建議用戶檢查訂單號或嘗試其他查詢方式
3. 保持回答簡潔且有用
<|im_end|>
<|im_start|>user
{question}
<|im_end|>
<|im_start|>assistant
"""

        try:
            response = self.model(
                prompt,
                max_tokens=512,
                temperature=0.1,
                stop=["<|im_end|>"]
            )
            
            # Handle response format properly
            if isinstance(response, dict) and 'choices' in response:
                ai_response = response['choices'][0]['text'].strip()
            else:
                return None
            
            # Only return response if it's meaningful
            if ai_response and len(ai_response) > 10:
                return ai_response
            
            return None
            
        except Exception as e:
            logger.error(f"AI processing error: {e}")
            return None 