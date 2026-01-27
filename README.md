# ATS Resume Match Analyzer

A professional-grade resume screening tool that analyzes how well your resume matches a job description. This application uses an 8-category scoring system to provide detailed, explainable matching analysis.

## 🎯 What This Does

Upload your resume and a job description, and get:
- **Overall Match Score** (0-100)
- **8-Category Breakdown** with individual scores
- **Keyword Matching** - shows what skills match and what's missing
- **Red Flags** - identifies potential concerns
- **Action Items** - recommendations to improve your match
- **Multiple Export Formats** - download results as JSON, Markdown, or PDF

## ✨ Key Features

✅ **Explainable Scoring** - Every score includes detailed reasoning  
✅ **Fast Processing** - Results in under 1 second  
✅ **No External APIs** - Completely offline, runs locally  
✅ **Multiple File Formats** - Supports PDF, DOCX, and TXT resumes  
✅ **Customizable Weights** - Adjust scoring importance via admin panel  
✅ **Professional Reports** - Export results in multiple formats  
✅ **Strict Mode** - Enforce high-quality matching standards  

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.9 or higher
- Node.js 16 or higher
- Git

### Installation

```bash
# 1. Navigate to project directory
cd Resume-screening-app-project

# 2. Run automated setup (one command!)
bash setup.sh

# This will:
# - Create Python virtual environment
# - Install Python dependencies
# - Install Node.js packages
# - Configure everything automatically
```

### Running the Application

#### Terminal 1 - Start Backend API

```bash
cd backend
source venv/bin/activate    # On Windows: venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see: `Uvicorn running on http://127.0.0.1:8000`

#### Terminal 2 - Start Frontend UI

```bash
cd frontend
npm run dev
```

You should see: `Local: http://localhost:5173`

### Access the App

Open your browser and go to: **http://localhost:5173**

## 📋 How to Test the Application

### Test Case 1: Basic Functionality

1. **Open the app** at http://localhost:5173
2. **Enter a resume** (paste text or upload PDF/DOCX)
3. **Enter a job description** (paste text)
4. **Click "Analyze"**
5. **View results:**
   - Overall score
   - 8 category scores
   - Matched keywords
   - Missing keywords
   - Red flags
   - Recommendations

### Test Case 2: Using Sample Data

The app includes pre-loaded sample data:

1. Click "📋 Load Sample Data" button
2. Pre-filled data appears:
   - Data Engineer resume (6+ years experience)
   - Senior Data Engineer job description
3. Click "Analyze"
4. Verify results appear correctly

### Test Case 3: Different File Formats

Test each file format:

#### PDF Resume
1. Click "Upload Resume" → Select any PDF
2. System extracts text from PDF
3. Click "Analyze"
4. Verify text was extracted correctly

#### Word Document (DOCX)
1. Click "Upload Resume" → Select any DOCX file
2. System extracts text from document
3. Click "Analyze"
4. Verify extraction is complete

#### Plain Text
1. Paste text directly in resume field
2. Click "Analyze"
3. Verify processing works

### Test Case 4: Export Formats

After analysis completes:

1. **Download as JSON**
   - Button: "📥 JSON"
   - Opens detailed JSON file
   - Contains all scoring data

2. **Download as Markdown**
   - Button: "📥 Markdown"
   - Opens readable formatted report
   - Good for sharing

3. **Download as PDF**
   - Button: "📥 PDF"
   - Professional formatted report
   - Color-coded scores
   - Ready to share with others

### Test Case 5: Admin Panel

Test customization features:

1. Click "⚙️ Admin Panel" (top right)
2. Adjust scoring weight sliders:
   - Keyword Skills: 0-100%
   - Experience Relevance: 0-100%
   - Role Match: 0-100%
   - etc.
3. Scroll down to see feature flags
4. Go back to form
5. Load sample data again
6. Verify new weights affect the score

### Test Case 6: Edge Cases

Try these scenarios to test robustness:

#### Empty Inputs
- Try analyzing with empty resume field
- Should show error message
- Try empty job description
- Should show error message

#### Very Short Inputs
- Resume: "Software Engineer"
- Job: "Looking for engineer"
- Should still produce results

#### No Matching Keywords
- Resume with completely different skills
- Job in different industry
- Should show low score
- Should show red flags

#### Perfect Match
- Copy job description into resume field
- Should show high score (90+)
- Most keywords should match

### Test Case 7: Strict Mode

1. Go to Analysis Form
2. Find "Strict Mode" toggle (near bottom)
3. **Disabled (OFF)**: More lenient matching
   - Partial keyword matches count
   - 50+ is "good match"

4. **Enabled (ON)**: Strict matching
   - Only exact matches count
   - Requires higher skill levels
   - 50+ is "excellent match"

5. Load sample data, toggle Strict Mode
6. Re-analyze to see score differences

## 🧪 Running Automated Tests

The application includes comprehensive unit tests:

```bash
cd backend

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_scoring_engine.py -v

# Run tests with coverage report
pytest tests/ --cov=app --cov-report=html
```

### Expected Test Results
- 15+ tests should pass
- All scoring categories tested
- File parsing tested
- Integration tests included

## 📊 Understanding the Scores

### Overall Score (0-100)
- **0-19**: No match - Look elsewhere
- **20-49**: Poor match - Major changes needed
- **50-79**: Good match - Competitive candidate
- **80-100**: Excellent match - Strong fit

### 8 Scoring Categories

| Category | Weight | Explanation |
|----------|--------|-------------|
| **Keyword & Skills** | 30% | How many required skills match |
| **Experience Relevance** | 20% | Relevance of your experience |
| **Role/Title Match** | 10% | Your title matches the role |
| **Seniority/Years** | 10% | Years of experience match |
| **Education/Certs** | 10% | Degrees and certifications |
| **Tooling/Stack** | 10% | Technical tools and languages |
| **Recency** | 5% | How recent your experience is |
| **Red Flags** | 5% | Negative indicators (-points) |

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Python web framework
- **Pydantic** - Data validation
- **pdfplumber** - PDF text extraction
- **python-docx** - Word document parsing
- **reportlab** - PDF report generation

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Vite** - Lightning-fast build tool
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client

### Testing
- **pytest** - Python testing framework
- Comprehensive test fixtures
- 15+ unit tests

## 📁 Project Structure

```
Resume-screening-app-project/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI application
│   │   ├── scoring_engine.py # Core scoring logic
│   │   ├── file_parser.py    # PDF/DOCX/TXT parsing
│   │   ├── pdf_generator.py  # Report generation
│   │   └── config.py         # Settings
│   ├── tests/
│   │   ├── test_scoring_engine.py
│   │   └── fixtures/
│   │       ├── sample_resume.txt
│   │       └── sample_jd.txt
│   ├── requirements.txt
│   ├── .env.example
│   └── venv/                 # Virtual environment (after setup)
│
├── frontend/
│   ├── src/
│   │   ├── pages/           # Page components
│   │   ├── api/            # API client
│   │   ├── types/          # TypeScript types
│   │   ├── App.tsx         # Main app
│   │   └── main.tsx        # Entry point
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── node_modules/        # Dependencies (after npm install)
│
├── Documentation/
│   ├── README.md           # This file
│   ├── QUICK_START.md      # 5-minute guide
│   ├── ARCHITECTURE.md     # Technical details
│   ├── GETTING_STARTED.md  # Commands reference
│   └── ... (other docs)
│
└── Configuration/
    ├── Makefile           # Development commands
    ├── setup.sh          # One-command setup
    └── .gitignore        # Git configuration
```

## 🔧 Configuration

### Environment Variables

Create `.env` file in backend directory:

```
# Server
UVICORN_HOST=0.0.0.0
UVICORN_PORT=8000

# CORS
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
```

See `backend/.env.example` for full configuration options.

## 🐛 Troubleshooting

### Issue: Port 8000 already in use
```bash
# Kill the process using port 8000
# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# On Mac/Linux:
lsof -i :8000
kill -9 <PID>
```

### Issue: npm modules not installing
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue: Python virtual environment not activating
```bash
# Delete and recreate
cd backend
rm -rf venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: PDF parsing fails
- Ensure pdfplumber is installed: `pip install pdfplumber`
- Try a simple PDF first (some PDFs have special encoding)
- Fallback to copying text manually

### Issue: Port 5173 not responding
```bash
# In frontend directory:
npm run dev -- --host 0.0.0.0 --port 5173
```

## 📈 Improving Your Resume Score

### Top Tips to Increase Match

1. **Match Keywords** - Use exact keywords from job description
2. **Update Dates** - Recent experience scores higher
3. **Add Specific Skills** - List all technical tools mentioned
4. **Quantify Achievements** - Use numbers and metrics
5. **Match Title** - Use similar job titles
6. **Add Education** - Include relevant degrees/certs
7. **Clean Formatting** - Ensure clean text extraction
8. **Avoid Red Flags** - No unexplained employment gaps

## 🔐 Privacy & Security

- ✅ **100% Local Processing** - Nothing uploaded to servers
- ✅ **No Data Retention** - Results deleted when browser closes
- ✅ **No Analytics** - No tracking or monitoring
- ✅ **No External APIs** - No third-party service calls
- ✅ **Open Source** - Review the code yourself

## 📚 Documentation

For detailed information, see:

- **[QUICK_START.md](QUICK_START.md)** - 5-minute reference
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical deep dive
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Command reference
- **[INDEX.md](INDEX.md)** - Complete documentation index

## 🚀 Next Steps (After Testing)

When ready to move forward:

1. **Test with your own data** - Use real resume and job
2. **Fine-tune weights** - Adjust in admin panel
3. **Export results** - Download as PDF to share
4. **Deploy to production** - See GITHUB_PUSH_GUIDE.md
5. **Customize further** - Modify scoring in backend

## 💡 Use Cases

### For Job Seekers
- ✅ Optimize resume before applying
- ✅ Understand what's missing
- ✅ Track improvement over time

### For Recruiters
- ✅ Quick initial screening
- ✅ Identify top candidates
- ✅ Reduce manual review time

### For HR Teams
- ✅ Standardize scoring
- ✅ Faster hiring cycles
- ✅ Better candidate data

## 📞 Support

### Getting Help

1. **Read Documentation** - Check QUICK_START.md or ARCHITECTURE.md
2. **Check Troubleshooting** - See section above
3. **Review Test Cases** - See how features work
4. **Examine Code** - Well-commented source code

### Common Questions

**Q: Is this production-ready?**  
A: Yes, all components are tested and documented.

**Q: Can I modify the scoring?**  
A: Yes, edit scoring weights in admin panel or code in `backend/app/scoring_engine.py`.

**Q: Can I add more file formats?**  
A: Yes, add parsing logic in `backend/app/file_parser.py`.


## 📝 License

See LICENSE file for details.

## 🎓 Learning Resources

The code includes:
- Clear function documentation
- Type hints (TypeScript & Python)
- Comprehensive test examples
- Well-organized file structure

---

**Ready to test?** Start with the **Quick Start** section above! 🚀