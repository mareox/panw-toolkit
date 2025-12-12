@echo off
REM Setup script for Prisma Access Mobile Users DNS Updater (Windows)

echo ==========================================
echo Prisma Access MU DNS Updater - Setup
echo ==========================================
echo.

REM Check Python version
echo [1/5] Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.7 or higher.
    pause
    exit /b 1
)
echo.

REM Create virtual environment
echo [2/5] Creating virtual environment...
python -m venv mudns
echo.

REM Activate virtual environment
echo [3/5] Activating virtual environment...
call mudns\Scripts\activate.bat
echo.

REM Install dependencies
echo [4/5] Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.

REM Setup configuration files
echo [5/5] Setting up configuration files...

if not exist "config\config.yaml" (
    copy config\config.yaml.template config\config.yaml
    echo Created config\config.yaml from template
    echo WARNING: Please edit config\config.yaml with your API credentials
) else (
    echo config\config.yaml already exists, skipping...
)

if not exist "config\domains.csv" (
    copy config\domains.csv.example config\domains.csv
    echo Created config\domains.csv from example
    echo WARNING: Please edit config\domains.csv with your internal domains
) else (
    echo config\domains.csv already exists, skipping...
)

REM Create directories
if not exist "logs" mkdir logs
if not exist "backup" mkdir backup

echo.
echo ==========================================
echo Setup complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Edit config\config.yaml with your Prisma Access credentials
echo 2. Edit config\domains.csv with your internal domains
echo 3. Run a dry-run test:
echo    python main.py --dry-run -v
echo 4. Apply changes:
echo    python main.py
echo.
echo To activate the virtual environment in the future:
echo    mudns\Scripts\activate.bat
echo.

pause
