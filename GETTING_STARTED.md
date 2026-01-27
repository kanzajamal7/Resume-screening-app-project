# 🚀 Getting Started - Command Reference

## Quick Commands

### Complete Setup (One Command)
```bash
bash setup.sh
```

### Or Manual Setup

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

**Frontend (separate terminal):**
```bash
cd frontend
npm install
npm run dev
```

### Using Makefile
```bash
make install       # Install all dependencies
make backend-dev   # Start backend (Terminal 1)
make frontend-dev  # Start frontend (Terminal 2)
make test         # Run all tests
```

---

## Testing

```bash
cd backend
pytest tests/ -v
```

Expected: ✅ 15+ tests PASSED

---

## Access Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Directory Structure

```
Resume-screening-app-project/
├── backend/              # Python/FastAPI
├── frontend/             # React/TypeScript
├── shared/              # (For future)
└── [Documentation files]
```

---

## What to Test First

1. **Sample Analysis**
   - Click "Load Sample Data"
   - Click "Analyze Resume"
   - See results appear

2. **File Upload**
   - Upload a PDF/DOCX resume
   - Enter job description
   - View results

3. **Admin Panel**
   - Navigate to `/admin`
   - Adjust scoring weights
   - See feature flags

4. **Export Reports**
   - Download as JSON
   - Download as Markdown
   - Download as PDF

---

## Troubleshooting

### Port in Use
```bash
# Find what's using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>
```

### Missing Dependencies
```bash
# Backend
pip install -r backend/requirements.txt

# Frontend
npm install --prefix frontend
```

### Clear Cache
```bash
# Backend
cd backend && rm -rf __pycache__ .pytest_cache

# Frontend
cd frontend && rm -rf node_modules dist
```

---

## File Locations

| What | Where |
|-----|-------|
| Scoring Logic | `backend/app/scoring_engine.py` |
| API Routes | `backend/app/main.py` |
| Main Component | `frontend/src/App.tsx` |
| Analysis Form | `frontend/src/pages/AnalysisForm.tsx` |
| Tests | `backend/tests/test_scoring_engine.py` |

---

## Documentation

- **QUICK_START.md** - 5-minute guide
- **ARCHITECTURE.md** - Technical details
- **FINAL_SUMMARY.md** - Complete overview
- **GITHUB_PUSH_GUIDE.md** - Deployment steps

---

## Key Endpoints

```bash
# Analyze
POST /api/analyze

# Get weights
GET /api/admin/weights

# Export
GET /api/report/{id}/json
GET /api/report/{id}/markdown
GET /api/report/{id}/pdf

# Health
GET /api/health
```

---

## Environment Variables (.env)

See `backend/.env.example` for all options.

Default settings work for development without changes.

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Backend won't start | Check port 8000 is free |
| Frontend won't start | Check port 5173 is free |
| PDF upload fails | Run `pip install --upgrade pdfplumber` |
| Tests fail | Run from `backend/` directory |
| CORS error | Backend port must be 8000 |

---

## Next Steps

1. ✅ Run application
2. ✅ Test with sample data
3. ✅ Run tests
4. ✅ Explore admin panel
5. ✅ Push to GitHub
6. ✅ Deploy to production

---

## Support

- Check **QUICK_START.md** for setup issues
- Check **ARCHITECTURE.md** for how things work
- Check code comments for implementation details
- Run tests to verify everything works

---

**Ready to go! 🚀**

Start with:
```bash
bash setup.sh
make backend-dev
# In another terminal:
make frontend-dev
```

Then visit: http://localhost:5173
