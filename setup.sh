#!/bin/bash
# Result Analytics — Quick Setup Script
set -e

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║     Result Analytics — Setup Script          ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
  echo "❌ Python 3 is required. Please install it and retry."
  exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Create virtual environment
if [ ! -d "venv" ]; then
  echo "📦 Creating virtual environment..."
  python3 -m venv venv
fi

# Activate
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip -q
pip install django pandas openpyxl Pillow xhtml2pdf -q
# xhtml2pdf is pure Python and works on all platforms including Windows
echo "✅ PDF export ready (xhtml2pdf — pure Python, Windows/Mac/Linux compatible)"

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate --run-syncdb

# Load demo data
echo ""
read -p "  Load demo student/result data? (y/n): " load_demo
if [[ "$load_demo" =~ ^[Yy]$ ]]; then
  python manage.py load_demo_data
fi

# Create superuser prompt
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Optional: Create a Django admin superuser"
echo "  (Press Ctrl+C to skip)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python manage.py createsuperuser || echo "  Skipped superuser creation."

# Done
echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║     ✅ Setup Complete!                        ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "  Start the server:  source venv/bin/activate && python manage.py runserver"
echo "  Load demo data:    python manage.py load_demo_data"
echo "  Open in browser:   http://127.0.0.1:8000"
echo ""
