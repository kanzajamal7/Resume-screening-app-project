# ATS Resume Match Analyzer - Complete Architecture & Implementation Guide

## 📋 Project Overview

This is a production-ready full-stack web application for analyzing resume-to-job-description matching using explainable scoring logic. It requires no external paid services and runs entirely locally.

## 🏗️ System Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface (React)                    │
│  - Resume upload/paste form                                  │
│  - JD text input                                             │
│  - Settings panel (strict mode, weights)                     │
│  - Results visualization                                     │
└────────────────────────┬────────────────────────────────────┘
                         │ (HTTP/REST)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Python)                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ File Parser (PDF/DOCX/TXT)                           │   │
│  │ - pdfplumber for PDF extraction                      │   │
│  │ - python-docx for Word documents                     │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Scoring Engine (Core Logic)                          │   │
│  │ - Text preprocessing                                 │   │
│  │ - Keyword extraction (must-have, nice-to-have)       │   │
│  │ - 8-category scoring                                 │   │
│  │ - Red flag detection                                 │   │
│  │ - Weighting & aggregation                            │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Report Generation                                    │   │
│  │ - JSON serialization                                 │   │
│  │ - Markdown formatting                                │   │
│  │ - PDF generation (reportlab)                         │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                         │ (In-memory storage, optional DB)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              In-Memory Analysis Storage                      │
│  (Stateless by default; can enable SQLite)                  │
└─────────────────────────────────────────────────────────────┘
```

## 📁 File Structure

```
resume-screening-app-project/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application & routes
│   │   ├── scoring_engine.py    # Core scoring logic (1000+ lines)
│   │   ├── file_parser.py       # PDF/DOCX text extraction
│   │   ├── pdf_generator.py     # PDF report generation
│   │   └── config.py            # Configuration management
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_scoring_engine.py  # 15+ unit tests
│   │   └── fixtures/
│   │       ├── sample_resume.txt
│   │       └── sample_jd.txt
│   ├── .env.example
│   ├── .gitignore
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable components (future)
│   │   ├── pages/
│   │   │   ├── AnalysisForm.tsx     # Resume + JD input form
│   │   │   ├── ResultsPage.tsx      # Results visualization
│   │   │   └── AdminPanel.tsx       # Settings & weights
│   │   ├── api/
│   │   │   └── client.ts        # API client wrapper
│   │   ├── types/
│   │   │   └── index.ts         # TypeScript interfaces
│   │   ├── App.tsx              # Main app component
│   │   ├── main.tsx             # React root
│   │   └── index.css            # Tailwind + custom styles
│   ├── public/
│   ├── .gitignore
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── postcss.config.js
├── shared/
│   └── (Future: shared types, scoring weights JSON)
├── Makefile                      # Development commands
├── setup.sh                      # One-command setup
├── README.md                     # Quick start guide
├── LICENSE                       # MIT License
└── .gitignore
```

## 🔬 Detailed Scoring Logic

### Text Preprocessing Phase

**Location**: `scoring_engine.py` > `TextPreprocessor`

1. **Normalization**
   - Convert to lowercase
   - Remove extra whitespace
   - Preserve punctuation for phrase matching

2. **Tokenization**
   - Extract individual words: `["python", "java", "sql"]`
   - Extract n-grams (2-3 word phrases): `["apache spark", "rest api"]`

3. **Evidence Extraction**
   - Find term positions in text
   - Extract context snippets (±10 words)
   - Used for explainability

### Keyword Extraction Phase

**Location**: `scoring_engine.py` > `KeywordExtractor`

#### From Job Description:

1. **Must-Have Keywords**
   - Lines containing: "must have", "required", "requirement", "minimum", "need", "experience with", "expertise in"
   - Extract technical terms, quoted phrases
   - Example: JD line "Must have 5+ years Python experience" → `["python", "5", "years"]`

2. **Nice-to-Have Keywords**
   - Lines containing: "preferred", "plus", "bonus", "nice to have", "additional", "beneficial"
   - Similar extraction process

3. **Technical Stack Matching**
   - Lookup against comprehensive dictionary:
     ```python
     TECH_STACK = {
       'languages': ['python', 'java', 'javascript', ...],
       'databases': ['mysql', 'postgresql', 'mongodb', ...],
       'cloud': ['aws', 'azure', 'gcp', ...],
       ...
     }
     ```
   - Case-insensitive matching
   - Capture uppercase acronyms (AWS, GCP, etc.)

4. **Years & Degree Extraction**
   - Regex patterns: `r'(\d+)\+?\s*years?'`, `r'(\d+)\s*-\s*(\d+)\s*years?'`
   - Degree keywords: bachelor, master, phd, certificate

### Resume Parsing Phase

**Location**: `scoring_engine.py` > `ResumeParser`

1. **Work Experience Extraction**
   - Regex pattern to find sections: "Experience", "Work History"
   - Parse job titles, date ranges, descriptions
   - Calculate years at each role, recency
   - Example output:
     ```python
     {
       'title': 'Senior Data Engineer',
       'start_year': 2022,
       'end_year': 2024,
       'years': 2,
       'recency': 0,
       'description': '...'
     }
     ```

2. **Education Extraction**
   - Find "Education" section
   - Extract degree types (bachelor, master, etc.)

3. **Total Years Calculation**
   - Sum of all `years` fields from experiences

### 8-Category Scoring

**Location**: `scoring_engine.py` > `ScoringEngine`

#### Category A: Keyword & Skills Match (Weight: 30%)

```
Algorithm:
1. Find matched must-haves in resume_text
   matched_must = count(must_have_kw in resume_text)
   
2. Find matched nice-to-haves in resume_text
   matched_nice = count(nice_to_have_kw in resume_text)
   
3. Calculate weighted score
   if must_haves exist:
       score = (matched_must / total_must) * 0.70 + (matched_nice / total_nice) * 0.30
   else:
       score = (matched_nice / total_nice) * 100
       
4. Clamp to 0-100 range
```

**Output**:
- Score: 0-100
- Details: matched counts
- Evidence: snippets for each matched keyword

#### Category B: Experience Relevance Match (Weight: 20%)

```
Algorithm:
1. Extract JD role keywords and technical terms
2. For each resume job:
   a. Calculate recency weight:
      if recency ≤ 3 years: weight = 1.0
      elif recency ≤ 7 years: weight = 0.7
      else: weight = 0.4
      
   b. Count keyword matches in job description
      matches = count(kw in job_description)
      
   c. Calculate relevance:
      relevance = (matches / total_keywords) * weight
      
3. Average across all jobs
   score = avg(relevance) * 100
```

**Output**:
- Score: 0-100
- Details: count of relevant recent experiences
- Evidence: list of high-impact roles

#### Category C: Role/Title Match (Weight: 10%)

```
Algorithm:
1. Extract all job titles from resume
2. Extract target role from JD (first meaningful line)
3. Scoring:
   - Exact match or substring match: 95+
   - Adjacent roles (contains "engineer", "developer", etc.): 70
   - No overlap: 20
```

#### Category D: Seniority/Years Match (Weight: 10%)

```
Algorithm:
1. Extract required_years from JD using regex
2. Calculate gap = resume_total_years - required_years
3. Scoring:
   - gap >= 0: min(100, 90 + gap*2)
   - gap >= -1: 70 + gap*15
   - gap < -1: max(0, 60 + gap*20)
```

#### Category E: Education/Certs Match (Weight: 10%)

```
Algorithm:
1. Extract required degrees from JD
2. Extract found degrees from resume
3. Calculate match ratio
   score = (matched_degrees / required_degrees) * 100
```

#### Category F: Tooling/Stack Match (Weight: 10%)

```
Algorithm:
1. Extract JD tools from TECH_STACK dictionary
2. Check which tools appear in resume
3. Calculate ratio
   score = (matched_tools / required_tools) * 100
```

#### Category G: Recency Match (Weight: 5%)

```
Algorithm:
1. Count resume jobs within last 3 years
2. Calculate ratio
   score = (recent_roles / total_roles) * 100
```

#### Category H: Red Flag Detection (Weight: 5%)

```
Algorithm:
Penalty system (deduct from 100):
- Each missing must-have: -15 points
- Job hopping (2+ roles <6 months): -20 points
- Unexplained gap >12 months: -20 points
- Over-claiming ("familiar" for required skills): -10 points

score = max(0, 100 - total_penalties)
```

**Output**:
- Score: 0-100 (where 100 = no red flags)
- Evidence: list of detected flags

### Overall Score Calculation

```
Algorithm:
1. Get all 8 category scores
2. Apply weights
   overall = Σ(category_score * category_weight)
   
3. Apply strict mode penalty (optional)
   if strict_mode and red_flags_count > 0:
       overall = max(0, overall - 20)
       
4. Determine label:
   if overall >= 75: "STRONG_MATCH"
   elif overall >= 50: "MEDIUM_MATCH"
   else: "WEAK_MATCH"
```

## 🔌 API Endpoints

### POST /api/analyze

**Request**:
```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "resume_text=..." \
  -F "jd_text=..." \
  -F "settings={\"strict_mode\": true}"
```

Or with file:
```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "resume_file=@resume.pdf" \
  -F "jd_text=..." \
  -F "settings={\"strict_mode\": true}"
```

**Response**:
```json
{
  "analysis_id": "2024-01-27T10-30-45-123456",
  "result": {
    "overall_score": 78.5,
    "label": "STRONG_MATCH",
    "categories": {...},
    "must_have": [...],
    "nice_to_have": [...],
    "red_flags": [],
    "actions": {...},
    "metadata": {...}
  }
}
```

### GET /api/report/{analysis_id}/json

Returns full analysis as JSON file (downloadable).

### GET /api/report/{analysis_id}/markdown

Returns formatted markdown report.

### GET /api/report/{analysis_id}/pdf

Returns professional PDF report with:
- Header with overall score/label
- Category breakdown with progress bars
- Keyword matching table
- Red flags section (if any)
- Recommendations
- Footer with metadata

## 🎯 Frontend Pages

### 1. AnalysisForm (Route: `/`)

**Components**:
- Resume input section (text/file toggle)
- JD input section
- Settings sidebar (strict mode toggle)
- Sample data button
- Submit button

**State**:
- resumeText
- resumeFile
- jdText
- strictMode
- loading
- error

**Actions**:
- Calls `analyzeResume()` API
- Navigates to `/results/{id}` with result data

### 2. ResultsPage (Route: `/results/:analysisId`)

**Display**:
- Score card (large, color-coded)
- Download buttons (JSON, Markdown, PDF)
- Category breakdown with progress bars
- Keyword matching section
- Red flags (if any)
- Recommendations section

**Features**:
- Expandable category details
- Evidence snippets inline
- Export functionality

### 3. AdminPanel (Route: `/admin`)

**Sections**:
- Scoring weights slider for each category
- Analysis settings (strict mode, feature flags)
- About scoring section
- Save/Reset buttons

**Notes**:
- Weights normalized to sum to 1.0
- Changes are in-memory only (can add DB persistence)

## 🧪 Testing Strategy

### Backend Tests (15+ tests)

**File**: `backend/tests/test_scoring_engine.py`

1. **Text Preprocessing** (3 tests)
   - Lowercase conversion
   - Whitespace normalization
   - Word/n-gram extraction

2. **Keyword Extraction** (5 tests)
   - Must-have extraction
   - Nice-to-have extraction
   - Years parsing
   - Degree extraction
   - Tech term extraction

3. **Resume Parsing** (3 tests)
   - Work experience extraction
   - Education extraction
   - Total years calculation

4. **Scoring Engine** (10+ tests)
   - Individual category scoring
   - Overall score calculation
   - Label assignment
   - Red flag detection
   - Strict mode penalties
   - Full end-to-end analysis

5. **Integration Tests**
   - Sample resume vs sample JD
   - Consistency across multiple runs

### Running Tests

```bash
cd backend
pytest tests/ -v
```

Expected output:
```
test_scoring_engine.py::TestTextPreprocessor::test_preprocess_lowercase PASSED
test_scoring_engine.py::TestKeywordExtractor::test_extract_must_haves PASSED
...
======================== 15 passed in 0.52s ========================
```

## Data Integrity & Verification

The system maintains strict accuracy standards:

### Strict Rules

1. **Keyword Suggestion**
   - Only suggest keywords from the JD or obvious synonyms
   - Do not invent skills not mentioned

2. **Evidence Requirements**
   - Every match includes text snippet from resume
   - Missing items clearly marked as "missing/unknown"

3. **Scoring Transparency**
   - Every score includes detailed reasoning
   - All logic is rule-based and explainable
   - No external services required

4. **Rewrite Suggestions**
   - Disabled by default (feature flag)
   - When enabled, uses only text from resume/JD
   - Never generates fictional work descriptions

## 🚀 Deployment Notes

### Development
```bash
# Terminal 1
cd backend && python -m uvicorn app.main:app --reload

# Terminal 2
cd frontend && npm run dev
```

### Production
```bash
# Build frontend
cd frontend && npm run build

# Run backend with gunicorn
cd backend && gunicorn -w 4 -b 0.0.0.0:8000 app.main:app

# Serve frontend build statically
```

### Docker
See `Dockerfile` and `docker-compose.yml` templates.

## 📈 Future Enhancements

- [ ] Database integration (SQLite/PostgreSQL)
- [ ] Batch processing (multiple resumes)
- [ ] Custom keyword dictionaries (user-editable JSON)
- [ ] Scoring rules editor UI
- [ ] Analytics dashboard (opt-in, anonymized)
- [ ] Multi-language support
- [ ] API rate limiting
- [ ] WebSocket for long-running analyses

---

**Last Updated**: 2024-01-27  
**Version**: 1.0.0  
**Status**: Production Ready
