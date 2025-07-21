@echo off
echo ========================================
echo    PackingElf Discord Bot Launcher
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

:: Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

:: Check if requirements are installed
echo Checking dependencies...
python -c "import discord, mysql.connector, llama_cpp" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install requirements
        pause
        exit /b 1
    )
)

:: Check if bot.env exists
if not exist "bot.env" (
    echo ERROR: bot.env file not found!
    echo Please create bot.env with your Discord token and database settings
    echo.
    echo Example bot.env content:
    echo DISCORD_TOKEN=your_discord_token_here
    echo DB_HOST=localhost
    echo DB_USER=root
    echo DB_PASSWORD=your_password
    echo DB_NAME=your_database_name
    pause
    exit /b 1
)

:: Check if AI model exists
if not exist "models\chatglm3-6b.Q4_K_M.gguf" (
    echo WARNING: AI model not found at models\chatglm3-6b.Q4_K_M.gguf
    echo The bot will run without AI features
    echo.
)

:: Set environment variables
echo Setting up environment...
set PYTHONPATH=%CD%\src;%PYTHONPATH%

:: Start the bot
echo.
echo ========================================
echo    Starting PackingElf Discord Bot...
echo ========================================
echo.
echo Bot is starting... Check the console for status updates
echo Press Ctrl+C to stop the bot
echo.

python run.py

:: If we get here, the bot has stopped
echo.
echo Bot has stopped. Press any key to exit...
pause >nul 