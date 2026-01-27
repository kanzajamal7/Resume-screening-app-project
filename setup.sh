#!/bin/bash
# Setup script for ATS Resume Match Analyzer

set -e

echo "🚀 ATS Resume Match Analyzer - Setup Script"
echo "==========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check Node
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

echo "✓ Python $(python3 --version | awk '{print $2}')"
echo "✓ Node $(node --version)"
echo ""

# Backend setup
echo "📦 Setting up backend..."
cd backend
pip install -r requirements.txt
cp .env.example .env
echo "✓ Backend setup complete"
cd ..

# Frontend setup
echo "📦 Setting up frontend..."
cd frontend
npm install
echo "✓ Frontend setup complete"
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo ""
echo "  Terminal 1: cd backend && python -m uvicorn app.main:app --reload"
echo "  Terminal 2: cd frontend && npm run dev"
echo ""
echo "Then visit http://localhost:5173"
