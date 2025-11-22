@echo off
REM Quick start script for Windows

echo Starting Skill Assessment API...
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found. Creating...
    python -m venv venv
    echo.
)

REM Activate virtual environment
call venv\Scripts\activate

REM Check if .env exists
if not exist ".env" (
    echo .env file not found!
    echo Please create a .env file with your OpenAI API key.
    echo You can copy .env.example to .env and edit it.
    pause
    exit /b
)

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt
echo.

REM Start the server
echo Starting FastAPI server...
echo API will be available at http://localhost:8000
echo API docs at http://localhost:8000/docs
echo.
python main.py

