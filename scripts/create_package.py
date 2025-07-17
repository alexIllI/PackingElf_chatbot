#!/usr/bin/env python3
"""
Package creator for ChatGLM3 Discord Bot
Creates a deployment package for distribution to user computers
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def create_deployment_package():
    """Create a deployment package for the bot"""
    
    # Package name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"chatglm3-discord-bot_v1.0_{timestamp}"
    
    # Files to include in the package
    include_files = [
        'main.py',
        'requirements.txt',
        'setup.py',
        'env.example',
        'config_validator.py',
        'install.bat',
        'install.sh',
        'README.md',
        'chatglm_3_discord_bot_setup.md'
    ]
    
    # Directories to include
    include_dirs = [
        'startup'
    ]
    
    # Files to exclude
    exclude_patterns = [
        '__pycache__',
        '*.pyc',
        '.env',
        'logs/*',
        'models/*',
        'chatglmbot-env',
        '*.zip',
        '.git',
        '.gitignore'
    ]
    
    print(f"📦 Creating deployment package: {package_name}")
    
    # Create package directory
    package_dir = Path(package_name)
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # Copy files
    for file_path in include_files:
        if Path(file_path).exists():
            shutil.copy2(file_path, package_dir)
            print(f"   ✅ Copied: {file_path}")
        else:
            print(f"   ⚠️  Missing: {file_path}")
    
    # Copy directories
    for dir_path in include_dirs:
        if Path(dir_path).exists():
            shutil.copytree(dir_path, package_dir / dir_path)
            print(f"   ✅ Copied directory: {dir_path}")
        else:
            print(f"   ⚠️  Missing directory: {dir_path}")
    
    # Create deployment instructions
    create_deployment_instructions(package_dir)
    
    # Create zip file
    zip_filename = f"{package_name}.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(package_dir)
                zipf.write(file_path, arcname)
    
    # Clean up
    shutil.rmtree(package_dir)
    
    print(f"\n✅ Deployment package created: {zip_filename}")
    print(f"📁 Package size: {os.path.getsize(zip_filename) / (1024*1024):.1f} MB")
    
    return zip_filename

def create_deployment_instructions(package_dir):
    """Create deployment instructions for users"""
    
    instructions = """# ChatGLM3 Discord Bot - Deployment Instructions

## Quick Start (Windows)

1. **Extract the package** to a folder on your computer
2. **Run the installer**: Double-click `install.bat`
3. **Configure the bot**: Edit the `.env` file with your settings
4. **Download the AI model**: 
   - Go to: https://huggingface.co/TheBloke/ChatGLM3-6B-GGUF
   - Download: `chatglm3-6b.Q4_0.gguf`
   - Place it in the `models/` folder
5. **Start the bot**: Run `python main.py`

## Quick Start (Linux/Mac)

1. **Extract the package** to a folder on your computer
2. **Make installer executable**: `chmod +x install.sh`
3. **Run the installer**: `./install.sh`
4. **Configure the bot**: Edit the `.env` file with your settings
5. **Download the AI model**: 
   - Go to: https://huggingface.co/TheBloke/ChatGLM3-6B-GGUF
   - Download: `chatglm3-6b.Q4_0.gguf`
   - Place it in the `models/` folder
6. **Start the bot**: `python main.py`

## Prerequisites

- Python 3.10 or higher
- MySQL database server
- Discord bot token
- At least 8GB RAM (16GB recommended)
- 10GB free disk space

## Configuration

Edit the `.env` file with your settings:

```env
# Discord Bot Token
DISCORD_TOKEN=your_bot_token_here

# MySQL Database
MYSQL_HOST=localhost
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database

# AI Model Path
MODEL_PATH=models/chatglm3-6b.Q4_0.gguf
```

## Auto-Startup Setup

### Windows
- Copy `startup/startup.bat` to Windows Startup folder
- Or run: `startup/startup.bat`

### Linux
- Use systemd service: `sudo systemctl enable chatglm3-bot.service`
- Or add to crontab: `@reboot /path/to/startup.sh`

## Troubleshooting

1. **Check configuration**: Run `python config_validator.py`
2. **View logs**: Check `logs/bot.log`
3. **Common issues**: See README.md for detailed troubleshooting

## Support

For issues and questions, check the documentation or contact support.
"""
    
    with open(package_dir / "DEPLOYMENT_INSTRUCTIONS.md", 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print("   ✅ Created: DEPLOYMENT_INSTRUCTIONS.md")

def create_minimal_package():
    """Create a minimal package without large files"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"chatglm3-discord-bot_minimal_v1.0_{timestamp}"
    
    # Minimal files for deployment
    minimal_files = [
        'main.py',
        'requirements.txt',
        'env.example',
        'config_validator.py',
        'install.bat',
        'install.sh',
        'DEPLOYMENT_INSTRUCTIONS.md'
    ]
    
    print(f"📦 Creating minimal package: {package_name}")
    
    # Create package directory
    package_dir = Path(package_name)
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # Copy minimal files
    for file_path in minimal_files:
        if Path(file_path).exists():
            shutil.copy2(file_path, package_dir)
            print(f"   ✅ Copied: {file_path}")
    
    # Create zip
    zip_filename = f"{package_name}.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(package_dir)
                zipf.write(file_path, arcname)
    
    shutil.rmtree(package_dir)
    
    print(f"\n✅ Minimal package created: {zip_filename}")
    print(f"📁 Package size: {os.path.getsize(zip_filename) / 1024:.1f} KB")
    
    return zip_filename

if __name__ == "__main__":
    print("🚀 ChatGLM3 Discord Bot Package Creator")
    print("=" * 50)
    
    # Create deployment instructions first
    create_deployment_instructions(Path("temp"))
    shutil.rmtree("temp")
    
    # Create packages
    print("\n1. Creating full deployment package...")
    full_package = create_deployment_package()
    
    print("\n2. Creating minimal package...")
    minimal_package = create_minimal_package()
    
    print("\n" + "=" * 50)
    print("✅ Package creation completed!")
    print(f"📦 Full package: {full_package}")
    print(f"📦 Minimal package: {minimal_package}")
    print("\n💡 Use the minimal package for faster downloads")
    print("💡 Use the full package for complete offline installation") 