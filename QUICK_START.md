# 🚀 Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 2. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 3. Open Browser

Visit: **http://localhost:5173**

## Usage Example

1. **Paste Resume Text**
   - Copy your resume content into the left textarea
   - Or upload a PDF/DOCX file

2. **Paste Job Description**
   - Copy the job description into the right textarea
   - Or click "Load Sample Data" to test

3. **Click "Analyze Resume"**
   - Wait for results (typically <1 second)

4. **View Results**
   - See overall score with label
   - Review 8 category breakdown
   - Check keyword matches
   - Read recommendations

5. **Export Report**
   - Download as JSON, Markdown, or PDF
   - Share with team or keep for records

## Common Commands

### Development
```bash
make install       # Install dependencies
make backend-dev   # Run backend
make frontend-dev  # Run frontend
make test         # Run tests
```

### Testing
```bash
cd backend
pytest tests/ -v   # Run all backend tests
```

### Clean Up
```bash
make clean        # Remove generated files
```

## API Examples

### Analyze Resume

```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "resume_text=John Doe..." \
  -F "jd_text=Senior Engineer..." \
  -F "settings={\"strict_mode\": true}"
```

### Download Reports

```bash
# JSON
curl http://localhost:8000/api/report/{analysis_id}/json > report.json

# Markdown
curl http://localhost:8000/api/report/{analysis_id}/markdown > report.md

# PDF
curl http://localhost:8000/api/report/{analysis_id}/pdf > report.pdf
```

## Scoring Explained

| Score | Label | Interpretation |
|-------|-------|-----------------|
| 80-100 | 🟢 STRONG MATCH | Excellent fit, apply now |
| 50-79 | 🟡 MEDIUM MATCH | Good potential, tailor resume |
| 0-49 | 🔴 WEAK MATCH | Significant gaps, reconsider |

## Understanding Results

### Categories (with weights)

- **A) Keyword & Skills (30%)**: Percentage of required skills found
- **B) Experience (20%)**: How relevant past roles are
- **C) Role/Title (10%)**: Title alignment
- **D) Seniority (10%)**: Years of experience match
- **E) Education (10%)**: Degree/cert requirements
- **F) Tools/Stack (10%)**: Technical stack overlap
- **G) Recency (5%)**: Recent relevant experience
- **H) Red Flags (5%)**: Missing must-haves, gaps, etc.

### Red Flags
- ❌ Missing critical requirements
- ❌ Employment gaps > 12 months
- ❌ Job hopping (multiple <6 month roles)
- ❌ Over-claiming skills

## Troubleshooting

### Port Already in Use

```bash
# Find process on port 8000
lsof -i :8000

# Kill it
kill -9 <PID>
```

### PDF Upload Not Working

Install pdfplumber:
```bash
pip install --upgrade pdfplumber
```

### Frontend Not Connecting

Check CORS - ensure backend is running on port 8000.

## Features

✅ File upload (PDF, DOCX, TXT)  
✅ Text paste input  
✅ 8-category scoring  
✅ Explainable results  
✅ Multiple export formats  
✅ Admin panel for weights  
✅ Red flag detection  
✅ Responsive design  
✅ No external APIs  
✅ Offline processing  

## File Locations

| Component | Location |
|-----------|----------|
| Scoring Logic | `backend/app/scoring_engine.py` |
| API Routes | `backend/app/main.py` |
| Frontend App | `frontend/src/App.tsx` |
| Analysis Form | `frontend/src/pages/AnalysisForm.tsx` |
| Results Display | `frontend/src/pages/ResultsPage.tsx` |
| Tests | `backend/tests/test_scoring_engine.py` |

## Next Steps

1. ✅ Run application
2. ✅ Test with sample data
3. ✅ Run tests to verify everything
4. ✅ Customize weights in Admin Panel
5. ✅ Deploy to production

## Documentation

- **README.md** - Overview & features
- **ARCHITECTURE.md** - Technical deep dive
- **IMPLEMENTATION_SUMMARY.md** - What was built
- **Code comments** - Inline documentation

## Need Help?

1. Check `ARCHITECTURE.md` for detailed info
2. Review sample resume/JD in test fixtures
3. Run tests to verify setup
4. Check browser console for frontend errors
5. Check terminal for backend logs

## Security Notes

- No data stored by default (stateless)
- All processing is local
- No third-party API calls
- HTTPS ready (use reverse proxy)

---

**Happy analyzing! 🎯**
