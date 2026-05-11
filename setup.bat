@echo off
echo.
echo ╔══════════════════════════════════════════════╗
echo ║     Result Analytics — Setup Script          ║
echo ╚══════════════════════════════════════════════╝
echo.

where python >nul 2>&1 || (echo ❌ Python not found. Please install Python 3 and retry. & pause & exit /b 1)

echo ✅ Python found.

if not exist venv (
  echo 📦 Creating virtual environment...
  python -m venv venv
)

call venv\Scripts\activate.bat

echo 📥 Installing dependencies...
pip install --upgrade pip -q
pip install django pandas openpyxl Pillow xhtml2pdf -q
echo ✅ All dependencies installed. PDF export uses xhtml2pdf (pure Python, Windows compatible).

echo 🗄️ Running migrations...
python manage.py migrate --run-syncdb

echo.
echo ╔══════════════════════════════════════════════╗
echo ║     ✅ Setup Complete!                        ║
echo ╚══════════════════════════════════════════════╝
echo.
echo   Start server:  venv\Scripts\activate ^& python manage.py runserver
echo   Open browser:  http://127.0.0.1:8000
echo.
pause
