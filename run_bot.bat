@echo off
echo Starting PackingElf Discord Bot...
echo.

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Set environment variables
set PYTHONPATH=%CD%\src;%PYTHONPATH%

:: Start the bot
python run.py

pause 