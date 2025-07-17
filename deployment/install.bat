@echo off
echo ========================================
echo ChatGLM3 Discord Bot Installer
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

:: Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python version: %PYTHON_VERSION%

:: Extract version number
for /f "tokens=2 delims=." %%a in ("%PYTHON_VERSION%") do set MAJOR_VERSION=%%a
if %MAJOR_VERSION% LSS 3 (
    echo ERROR: Python 3.10+ is required
    pause
    exit /b 1
)

:: Create virtual environment
echo.
echo Creating virtual environment...
if exist "chatglmbot-env" (
    echo Virtual environment already exists. Removing old one...
    rmdir /s /q "chatglmbot-env"
)
python -m venv chatglmbot-env
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

:: Activate virtual environment
echo Activating virtual environment...
call chatglmbot-env\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

:: Create necessary directories
echo Creating directories...
if not exist "models" mkdir models
if not exist "logs" mkdir logs
if not exist "startup" mkdir startup

:: Check if .env file exists
if not exist ".env" (
    echo.
    echo Creating .env file from template...
    copy "env.example" ".env"
    echo.
    echo IMPORTANT: Please edit the .env file with your configuration:
    echo - Discord bot token
    echo - MySQL database credentials
    echo - Model path
    echo.
    echo Opening .env file for editing...
    notepad .env
)

:: Check if model file exists
if not exist "models\chatglm3-6b.Q4_0.gguf" (
    echo.
    echo WARNING: ChatGLM3 model file not found!
    echo Please download chatglm3-6b.Q4_0.gguf from:
    echo https://huggingface.co/TheBloke/ChatGLM3-6B-GGUF
    echo And place it in the models/ directory
    echo.
)

:: Create startup script
echo Creating startup script...
(
echo @echo off
echo cd /d "%%~dp0"
echo call chatglmbot-env\Scripts\activate.bat
echo python main.py
echo pause
) > startup\startup.bat

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file with your configuration
echo 2. Download the AI model to models/ directory
echo 3. Run: python main.py
echo 4. For auto-startup, use: startup\startup.bat
echo.
pause 