.PHONY: help dev backend-dev frontend-dev test backend-test frontend-test install clean

help:
	@echo "ATS Resume Match Analyzer - Makefile Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  help              Show this help message"
	@echo "  dev               Run both backend and frontend (requires tmux/separate terminals)"
	@echo "  backend-dev       Run backend server only"
	@echo "  frontend-dev      Run frontend dev server only"
	@echo "  test              Run all tests"
	@echo "  backend-test      Run backend tests only"
	@echo "  frontend-test     Run frontend tests only"
	@echo "  install           Install all dependencies"
	@echo "  clean             Clean up generated files and cache"

install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✓ All dependencies installed"

backend-dev:
	@echo "Starting backend server..."
	cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend-dev:
	@echo "Starting frontend dev server..."
	cd frontend && npm run dev

backend-test:
	@echo "Running backend tests..."
	cd backend && pytest tests/ -v --tb=short

frontend-test:
	@echo "Running frontend tests..."
	cd frontend && npm run test

test: backend-test frontend-test

dev:
	@echo "To run both servers, use two separate terminals:"
	@echo ""
	@echo "Terminal 1: make backend-dev"
	@echo "Terminal 2: make frontend-dev"
	@echo ""
	@echo "Or on macOS/Linux with tmux:"
	@echo "tmux new-session -d -s ats-app 'make backend-dev'"
	@echo "tmux new-window -t ats-app -n frontend 'make frontend-dev'"
	@echo "tmux attach -t ats-app"

clean:
	@echo "Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	cd backend && rm -rf .pytest_cache build dist *.egg-info 2>/dev/null || true
	cd frontend && rm -rf node_modules dist .cache 2>/dev/null || true
	@echo "✓ Cleanup complete"

.DEFAULT_GOAL := help
