# ChatGLM3 Discord Bot - Deployment Guide

## Overview

This guide explains how to create robust deployment packages for the ChatGLM3 Discord Bot that will work reliably on user computers.

## Development vs Production Setup

### Development Environment (Your Computer)

- ✅ Full development tools
- ✅ Direct access to all files
- ✅ Easy debugging and testing
- ✅ Version control

### Production Environment (User Computers)

- ✅ Minimal dependencies
- ✅ Automated installation
- ✅ Error handling and validation
- ✅ Auto-startup capability

## Package Management Strategy

### 1. Version Pinning

All dependencies are pinned to specific versions to ensure consistency:

```txt
discord.py==2.3.2
mysql-connector-python==8.2.0
gpt4all==2.0.2
python-dotenv==1.0.0
```

### 2. Platform-Specific Dependencies

Windows-specific packages are conditionally installed:

```txt
pywin32==306; sys_platform == "win32"
```

### 3. Environment Validation

The `config_validator.py` checks:

- Python version compatibility
- Required packages installation
- Environment variables
- Database connectivity
- AI model file existence
- File permissions

## Creating Deployment Packages

### Option 1: Automated Package Creation

```bash
python create_package.py
```

This creates:

- **Full package**: Complete installation with documentation
- **Minimal package**: Core files only (faster download)

### Option 2: Manual Package Creation

1. **Core files** (always include):

   ```
   main.py
   requirements.txt
   env.example
   config_validator.py
   install.bat (Windows)
   install.sh (Linux/Mac)
   ```

2. **Optional files**:

   ```
   setup.py
   README.md
   chatglm_3_discord_bot_setup.md
   startup/ (directory)
   ```

3. **Exclude files**:
   ```
   .env (contains sensitive data)
   logs/ (user-specific)
   models/ (large files)
   chatglmbot-env/ (user-specific)
   __pycache__/
   *.pyc
   ```

## Installation Process

### Windows Installation Flow

1. **User runs** `install.bat`
2. **Script checks** Python installation
3. **Creates** virtual environment
4. **Installs** dependencies from `requirements.txt`
5. **Creates** `.env` from `env.example`
6. **Opens** `.env` for user configuration
7. **Creates** startup scripts
8. **Validates** configuration

### Linux/Mac Installation Flow

1. **User runs** `./install.sh`
2. **Script checks** Python installation
3. **Creates** virtual environment
4. **Installs** dependencies
5. **Creates** `.env` from template
6. **Opens** editor for configuration
7. **Creates** systemd service (Linux)
8. **Sets** executable permissions

## Configuration Management

### Environment Variables

All configuration is externalized in `.env`:

```env
# Discord Bot
DISCORD_TOKEN=your_token_here

# Database
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DATABASE=database_name

# AI Model
MODEL_PATH=models/chatglm3-6b.Q4_0.gguf

# Bot Settings
COMMAND_PREFIX=!
MAX_RESULTS=100
LOG_LEVEL=INFO
```

### Validation Process

Before starting, the bot validates:

1. **System requirements** (Python version, memory)
2. **Dependencies** (all packages installed)
3. **Configuration** (environment variables set)
4. **Resources** (model file, database access)
5. **Permissions** (file write access)

## Error Handling Strategy

### Installation Errors

- **Python not found**: Clear error message with download link
- **Dependency failure**: Detailed error with troubleshooting steps
- **Permission issues**: Instructions for running as administrator

### Runtime Errors

- **Configuration errors**: Validation before startup
- **Database errors**: Connection testing and retry logic
- **AI model errors**: Graceful degradation without model
- **Discord errors**: Token validation and connection handling

## Auto-Startup Implementation

### Windows Auto-Startup

1. **Startup folder method**:

   - Copy `startup/startup.bat` to `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`

2. **Windows Service method**:
   ```bash
   python startup/install_service.py
   ```

### Linux Auto-Startup

1. **Systemd service**:

   ```bash
   sudo cp startup/chatglm3-bot.service /etc/systemd/system/
   sudo systemctl enable chatglm3-bot.service
   sudo systemctl start chatglm3-bot.service
   ```

2. **Crontab method**:
   ```bash
   @reboot /path/to/startup/startup.sh
   ```

## Testing Deployment

### Pre-Deployment Testing

1. **Clean environment test**:

   ```bash
   # Create fresh virtual environment
   python -m venv test-env
   source test-env/bin/activate  # or test-env\Scripts\activate
   pip install -r requirements.txt
   python config_validator.py
   ```

2. **Package integrity test**:
   ```bash
   # Extract package and test installation
   unzip chatglm3-discord-bot_v1.0_*.zip
   cd chatglm3-discord-bot_v1.0_*
   ./install.sh  # or install.bat
   ```

### User Environment Testing

Test on different systems:

- **Windows 10/11** (different Python versions)
- **Ubuntu 20.04/22.04** (system Python vs pyenv)
- **macOS** (Intel and Apple Silicon)

## Troubleshooting Common Issues

### Installation Issues

1. **Python not in PATH**: Add Python to system PATH
2. **Permission denied**: Run as administrator (Windows) or use sudo (Linux)
3. **Network issues**: Check firewall and proxy settings

### Runtime Issues

1. **Model not loading**: Check file path and permissions
2. **Database connection**: Verify credentials and network access
3. **Discord token**: Ensure bot token is valid and has proper permissions

### Performance Issues

1. **Slow AI responses**: Reduce model complexity or increase system resources
2. **Memory usage**: Monitor with `psutil` and adjust settings
3. **Database queries**: Implement query optimization and caching

## Security Considerations

### Environment Security

- **Never commit** `.env` files to version control
- **Use dedicated** database user with minimal permissions
- **Validate** all user inputs before processing
- **Log** security-relevant events

### Deployment Security

- **Verify** package integrity before distribution
- **Use HTTPS** for downloads and updates
- **Implement** proper error handling to avoid information leakage
- **Regular** security updates for dependencies

## Monitoring and Maintenance

### Logging Strategy

- **Structured logging** with different levels
- **Log rotation** to prevent disk space issues
- **Error tracking** for debugging user issues

### Update Strategy

- **Version management** for easy rollbacks
- **Backward compatibility** for configuration changes
- **Migration scripts** for database schema changes

## Best Practices

### For Developers

1. **Test thoroughly** on target platforms
2. **Document** all configuration options
3. **Provide** clear error messages
4. **Include** troubleshooting guides

### For Users

1. **Follow** installation instructions exactly
2. **Keep** system requirements in mind
3. **Backup** configuration before updates
4. **Monitor** logs for issues

## Support and Documentation

### User Documentation

- **Quick start guide** for immediate setup
- **Detailed manual** for advanced configuration
- **FAQ** for common issues
- **Troubleshooting guide** for complex problems

### Developer Documentation

- **API documentation** for extending functionality
- **Architecture overview** for understanding the system
- **Deployment procedures** for consistent releases
- **Testing strategies** for quality assurance

---

This deployment strategy ensures that your ChatGLM3 Discord Bot can be reliably deployed to user computers with minimal setup issues and maximum functionality.
