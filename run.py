#!/usr/bin/env python3
"""
Main entry point for the ChatGLM3 Discord Database Bot.
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# Load environment variables from bot.env
def load_env_file():
    """Load environment variables from bot.env file."""
    env_file = Path(__file__).parent / "bot.env"
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print(f"✅ Loaded environment variables from {env_file}")
    else:
        print(f"⚠️ Environment file {env_file} not found")

# Load environment variables
load_env_file()

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from bot import create_bot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

def check_environment():
    """Check if required environment variables are set."""
    required_vars = ['DISCORD_TOKEN']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in your bot.env file or environment")
        return False
    
    return True

async def main():
    """Main function to run the bot."""
    logger.info("Starting ChatGLM3 Discord Database Bot...")
    
    # Check environment
    if not check_environment():
        logger.error("Environment check failed. Exiting.")
        return
    
    # Create and run bot
    bot = create_bot()
    
    try:
        logger.info("Initializing bot...")
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            logger.error("DISCORD_TOKEN is not set")
            return
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise
    finally:
        logger.info("Cleaning up...")
        await bot.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1) 