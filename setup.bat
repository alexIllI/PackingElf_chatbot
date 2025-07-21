@echo off
echo ========================================
echo    PackingElf Bot Setup Script
echo ========================================
echo.

:: Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found: 
python --version

:: Create virtual environment
echo.
echo Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
)

:: Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

:: Install requirements
echo.
echo Installing required packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)

:: Check bot.env
echo.
echo Checking configuration...
if not exist "bot.env" (
    echo.
    echo WARNING: bot.env file not found!
    echo Please create bot.env with the following content:
    echo.
    echo DISCORD_TOKEN=your_discord_token_here
    echo DB_HOST=localhost
    echo DB_USER=root
    echo DB_PASSWORD=your_password
    echo DB_NAME=your_database_name
    echo.
    echo You can copy bot.env.example and modify it if it exists
    echo.
) else (
    echo Configuration file found
)

:: Check AI model
echo.
echo Checking AI model...
if not exist "models\chatglm3-6b.Q4_K_M.gguf" (
    echo.
    echo WARNING: AI model not found!
    echo The bot will work without AI features
    echo To enable AI features, download the model to models\chatglm3-6b.Q4_K_M.gguf
    echo.
) else (
    echo AI model found
)

echo.
echo ========================================
echo    Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Configure bot.env with your Discord token and database settings
echo 2. Ensure your MySQL database is running
echo 3. Run start_bot.bat to start the bot
echo.
echo For help, check the README.md file
echo.
pause 