# ChatGLM3 Discord SQL Bot

## Purpose

Build a Discord chatbot that runs locally on your computer, supports Chinese questions converted to SQL, operates MySQL databases, and uses ChatGLM3 for local LLM processing. Designed for automation environments and easy deployment with auto-startup capabilities.

---

## Features

- 🤖 **AI-Powered**: Uses ChatGLM3-6B for intelligent question processing
- 🗄️ **Database Access**: Direct MySQL database connectivity
- 🇨🇳 **Chinese Support**: Native Chinese language processing
- 🔄 **Auto-Startup**: Runs automatically when computer starts
- 💬 **Discord Integration**: Seamless Discord bot functionality
- 🔒 **Local Processing**: All AI processing happens locally for privacy

---

## Project Structure

```
chatglm3-discord-bot/
├── src/                     # Source code
│   ├── __init__.py         # Package initialization
│   ├── main.py             # Main entry point
│   ├── bot.py              # Discord bot implementation
│   ├── config.py           # Configuration management
│   ├── database.py         # Database operations
│   └── ai_model.py         # AI model integration
├── tests/                   # Unit tests
├── docs/                    # Documentation
│   ├── chatglm_3_discord_bot_setup.md
│   └── DEPLOYMENT_GUIDE.md
├── scripts/                 # Build and utility scripts
│   └── create_package.py   # Package creation script
├── deployment/              # Deployment files
│   ├── install.bat         # Windows installer
│   └── install.sh          # Linux/Mac installer
├── models/                  # AI model files (not in repo)
│   └── chatglm3-6b.Q4_K_M.gguf
├── logs/                    # Application logs (not in repo)
├── venv/                    # Virtual environment (not in repo)
├── run.py                   # Application runner
├── requirements.txt         # Python dependencies
├── env.example             # Environment template
└── setup.py               # Package setup
```

---

## Prerequisites

- Python 3.10+
- pip package manager
- Discord bot token
- MySQL server (local or LAN)
- ChatGLM3-6B GGUF model (Q4_K_M recommended)
- Windows 10/11 (for auto-startup features)

---

## Development Setup

### 1. Clone and Setup Environment

```bash
# Navigate to project directory
cd PackingElf_chatbot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 2. Download ChatGLM3 GGUF Model

1. Visit HuggingFace: [mradermacher/chatglm3-6b-GGUF](https://huggingface.co/mradermacher/chatglm3-6b-GGUF)
2. Download `chatglm3-6b.Q4_K_M.gguf` (4.2GB, fast and recommended)
3. Create `models/` directory and place the file there

**Model Options:**

- **Q4_K_M** (4.2GB) - Fast, recommended for most use cases
- **Q4_K_S** (3.9GB) - Faster, slightly lower quality
- **Q5_K** (4.8GB) - Better quality, slower
- **Q6_K** (5.6GB) - Very good quality, slower

### 3. Configure Environment

```bash
# Copy environment template
cp env.example .env

# Edit configuration (use your preferred editor)
# Windows:
notepad .env
# Linux/Mac:
nano .env
```

### 4. Environment Configuration

Edit `.env` file with your settings:

```env
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_bot_token_here

# MySQL Database Configuration
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=your_database_name
MYSQL_PORT=3306

# AI Model Configuration
MODEL_PATH=models/chatglm3-6b.Q4_K_M.gguf

# Bot Configuration
COMMAND_PREFIX=!
MAX_RESULTS=100
LOG_LEVEL=INFO

# Performance Settings
AI_THREADS=0
AI_MEMORY_LIMIT=0

# Security Settings
LOG_QUERIES=true
ENABLE_CACHE=false
CACHE_EXPIRY=3600
```

---

## Running the Bot

### Development Mode

```bash
# Ensure virtual environment is activated
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac

# Run the bot
python run.py
```

### Production Mode

Use the deployment scripts in `deployment/` directory for production installation.

---

## Usage Examples

Once the bot is running, you can use these commands in Discord:

```
!query 过去七天有多少笔订单？
!query 显示所有用户信息
!query 统计每个部门的员工数量
!query 查找销售额最高的前10个产品
!status
!help
```

---

## Development Workflow

### Virtual Environment Management

```bash
# Always activate virtual environment before development
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install new dependencies
pip install package_name
pip freeze > requirements.txt

# Deactivate when done
deactivate
```

### Code Organization

- **`src/main.py`**: Application entry point and initialization
- **`src/bot.py`**: Discord bot logic and command handlers
- **`src/config.py`**: Configuration management and validation
- **`src/database.py`**: MySQL database operations
- **`src/ai_model.py`**: ChatGLM3 AI model integration

### Testing

```bash
# Run tests (when implemented)
python -m pytest tests/

# Run configuration validation
python -c "from src.config import ConfigManager; cm = ConfigManager(); print(cm.validate_required_keys())"
```

---

## Deployment to User Computers

### Create Deployment Package

```bash
# Activate virtual environment
venv\Scripts\activate

# Create deployment package
python scripts/create_package.py
```

### Package Contents

1. **Core files:**

   - All `src/` modules
   - `requirements.txt`
   - `env.example`
   - `run.py`

2. **Installation files:**

   - `deployment/install.bat` (Windows)
   - `deployment/install.sh` (Linux/Mac)

3. **Documentation:**
   - Setup and usage instructions
   - Troubleshooting guide

### User Installation

Users receive a ZIP package and follow these steps:

1. **Extract package** to desired location
2. **Run installer**: `install.bat` (Windows) or `./install.sh` (Linux/Mac)
3. **Configure**: Edit `.env` file with their settings
4. **Download model**: Get ChatGLM3 model file from [mradermacher/chatglm3-6b-GGUF](https://huggingface.co/mradermacher/chatglm3-6b-GGUF)
5. **Start bot**: `python run.py`

---

## Auto-Startup Setup

### Windows Auto-Startup

1. **Task Scheduler method** (recommended):

   - Open Task Scheduler
   - Create Basic Task
   - Set to run `run.py` at startup

2. **Startup folder method**:
   ```bash
   # Copy startup script to startup folder
   copy deployment\startup.bat "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
   ```

### Linux Auto-Startup

1. **Systemd service**:

   ```bash
   sudo cp deployment/chatglm3-bot.service /etc/systemd/system/
   sudo systemctl enable chatglm3-bot.service
   sudo systemctl start chatglm3-bot.service
   ```

2. **Crontab method**:
   ```bash
   crontab -e
   # Add: @reboot /path/to/run.py
   ```

---

## Use Cases

- **Business Intelligence**: Internal company database queries
- **Educational**: Database learning assistant for courses
- **Development**: Quick database exploration during development
- **Monitoring**: Automated database health checks

---

## Troubleshooting

### Common Issues

1. **Virtual environment not activated**: Always activate before running
2. **Import errors**: Ensure `src/` is in Python path
3. **Model not loading**: Check file path and permissions
4. **Database connection failed**: Verify credentials in `.env`
5. **Discord bot not responding**: Check bot token and permissions

### Debug Commands

```bash
# Test configuration
python -c "from src.config import ConfigManager; print('Config OK')"

# Test database connection
python -c "from src.database import DatabaseManager; dm = DatabaseManager(); print('DB:', dm.test_connection())"

# Check virtual environment
python -c "import sys; print('Virtual env:', 'venv' in sys.prefix)"
```

### Logs

Check `logs/bot.log` for detailed error information and debugging.

---

## Security Considerations

- **Virtual Environment**: Isolates dependencies from system Python
- **Environment Variables**: Keep sensitive data in `.env` file
- **Database Security**: Use dedicated database user with limited permissions
- **Regular Updates**: Keep dependencies updated for security patches

---

## Future Enhancements

- [ ] Query history and caching
- [ ] Result row limit controls
- [ ] Multiple database support
- [ ] Advanced SQL generation with table schema awareness
- [ ] Scheduled queries and alerts
- [ ] Web dashboard for query management
- [ ] Role-based access control
- [ ] Query performance monitoring
- [ ] Unit test coverage
- [ ] Docker containerization

---

This setup ensures a robust, maintainable, and deployable Discord bot with proper virtual environment isolation and clean code organization.
