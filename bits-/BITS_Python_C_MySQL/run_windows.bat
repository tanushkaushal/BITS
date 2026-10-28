@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  py -3 -m venv .venv
  if errorlevel 1 goto :error
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 goto :error
echo.
echo Configure your MySQL password in this terminal when prompted.
set /p BITS_DB_USER=MySQL username [root]: 
if "%BITS_DB_USER%"=="" set BITS_DB_USER=root
set /p BITS_DB_PASSWORD=MySQL password (input will be visible): 
set BITS_DB_HOST=localhost
set BITS_DB_PORT=3306
set BITS_DB_NAME=bits_inventory
set BITS_SECRET_KEY=replace-this-local-demo-secret-before-deployment
python app.py
if errorlevel 1 goto :error
goto :eof
:error
echo Setup or launch failed. Read the error above and check README.md.
pause
