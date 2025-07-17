# ChatGLM3 Discord SQL Bot

A Discord chatbot that uses ChatGLM3 AI to convert Chinese questions to SQL queries and execute them against MySQL databases.

## Features

- 🤖 AI-powered Chinese to SQL conversion using ChatGLM3
- 🗄️ Direct MySQL database connectivity
- 🔒 Local processing for privacy
- 🔄 Auto-startup capability
- 💬 Discord integration

## Quick Start

### Prerequisites

- Python 3.10+
- MySQL database
- Discord bot token

### Development Setup

```bash
# Clone and navigate to project
cd PackingElf_chatbot

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example .env
# Edit .env with your settings

# Download ChatGLM3 model to models/ directory
# Get from: https://huggingface.co/TheBloke/ChatGLM3-6B-GGUF

# Run the bot
python run.py
```

### Configuration

Edit `.env` file:

```env
DISCORD_TOKEN=your_discord_bot_token
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database
MODEL_PATH=models/chatglm3-6b.Q4_0.gguf
```

## Usage

Discord commands:

- `!query <question>` - Ask database questions in Chinese
- `!status` - Check bot status
- `!help` - Show help

Example:

```
!query 过去七天有多少笔订单？
!query 显示所有用户信息
```

## Project Structure

```
src/                    # Source code
├── main.py            # Entry point
├── bot.py             # Discord bot logic
├── config.py          # Configuration management
├── database.py        # Database operations
└── ai_model.py        # AI model integration

deployment/            # Installation scripts
docs/                  # Documentation
scripts/               # Build utilities
tests/                 # Unit tests
```

## Documentation

- [Full Setup Guide](docs/chatglm_3_discord_bot_setup.md)
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md)

## License

MIT License
