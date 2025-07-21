"""
ChatGLM3 Discord Bot - Main Entry Point
"""

import sys
import logging
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from bot import ChatGLM3Bot
from config import ConfigManager

def setup_logging():
    """Setup logging configuration"""
    # Create logs directory
    logs_dir = Path(__file__).parent.parent / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / 'bot.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def validate_environment():
    """Validate environment and configuration"""
    print("🔍 Validating environment...")
    
    # Check configuration
    config = ConfigManager()
    is_valid, missing_keys = config.validate_required_keys()
    
    if not is_valid:
        print("❌ Missing required configuration:")
        for key in missing_keys:
            print(f"   - {key}")
        print("\nPlease check your .env file and ensure all required values are set.")
        return False
    
    print("✅ Environment validation passed!")
    return True

def main():
    """Main function"""
    print("🚀 Starting ChatGLM3 Discord Bot...")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    
    # Validate environment
    if not validate_environment():
        sys.exit(1)
    
    # Create and run bot
    try:
        bot = ChatGLM3Bot()
        print("🤖 Bot initialized successfully!")
        print("🔗 Starting Discord connection...")
        bot.run()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 