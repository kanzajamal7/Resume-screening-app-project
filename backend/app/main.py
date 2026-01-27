"""
FastAPI application for ATS Resume Match Analyzer
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import tempfile
import os
import json
from datetime import datetime
import logging

from app.scoring_engine import ScoringEngine, to_dict
from app.file_parser import parse_resume_file, parse_text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ATS Resume Match Analyzer",
    description="Analyze resume match against job descriptions",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for storing analyses (in-memory, stateless by default)
# Can be extended with SQLite for persistence
analyses = {}


class AnalysisSettings(BaseModel):
    """Analysis configuration settings."""
    strict_mode: bool = False
    weights: Optional[Dict[str, float]] = None
    toggle_synonyms: bool = True
    toggle_rewrite_suggestions: bool = False


class AnalysisRequest(BaseModel):
    """Request body for analysis endpoint."""
    resume_text: str
    jd_text: str
    settings: Optional[AnalysisSettings] = None


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.post("/api/analyze")
async def analyze(
    jd_text: str = Form(...),
    resume_text: Optional[str] = Form(None),
    resume_file: Optional[UploadFile] = File(None),
    settings: Optional[str] = Form(None)
):
    """
    Analyze resume against job description.
    
    Accepts either:
    - resume_text: Plain text resume
    - resume_file: PDF, DOCX, or TXT file
    
    Required:
    - jd_text: Job description text
    
    Optional:
    - settings: JSON string with analysis settings
    """
    
    try:
        # Parse JD text
        if not jd_text or not jd_text.strip():
            raise HTTPException(status_code=400, detail="Job description is required")
        
        # Get resume text
        if resume_text:
            parsed_resume = resume_text.strip()
        elif resume_file:
            # Parse uploaded file
            file_content = await resume_file.read()
            file_extension = resume_file.filename.split('.')[-1].lower()
            parsed_resume = parse_resume_file(file_content, file_extension)
        else:
            raise HTTPException(
                status_code=400,
                detail="Either resume_text or resume_file is required"
            )
        
        if not parsed_resume or not parsed_resume.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from resume file"
            )
        
        # Parse settings
        analysis_settings = AnalysisSettings()
        if settings:
            try:
                settings_dict = json.loads(settings)
                analysis_settings = AnalysisSettings(**settings_dict)
            except json.JSONDecodeError:
                logger.warning("Invalid settings JSON, using defaults")
        
        # Create scoring engine
        engine = ScoringEngine(
            weights=analysis_settings.weights,
            strict_mode=analysis_settings.strict_mode
        )
        
        # Run analysis
        result = engine.analyze(parsed_resume, jd_text)
        
        # Convert to dictionary for JSON response
        result_dict = to_dict(result)
        
        # Store analysis (in-memory, can be extended to database)
        analysis_id = datetime.now().isoformat().replace(":", "-")
        analyses[analysis_id] = {
            'result': result_dict,
            'resume_text': parsed_resume,
            'jd_text': jd_text,
            'settings': analysis_settings.dict(),
            'created_at': datetime.now().isoformat()
        }
        
        return {
            'analysis_id': analysis_id,
            'result': result_dict
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/api/report/{analysis_id}/json")
async def get_json_report(analysis_id: str):
    """Download analysis result as JSON."""
    
    if analysis_id not in analyses:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis = analyses[analysis_id]
    
    return JSONResponse(
        content=analysis['result'],
        media_type="application/json"
    )


@app.get("/api/report/{analysis_id}/markdown")
async def get_markdown_report(analysis_id: str):
    """Download analysis result as Markdown."""
    
    if analysis_id not in analyses:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis = analyses[analysis_id]
    result = analysis['result']
    
    # Generate markdown
    markdown = _generate_markdown_report(result)
    
    return JSONResponse(
        content={
            'analysis_id': analysis_id,
            'markdown': markdown
        }
    )


@app.get("/api/report/{analysis_id}/pdf")
async def get_pdf_report(analysis_id: str):
    """Download analysis result as PDF."""
    
    if analysis_id not in analyses:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis = analyses[analysis_id]
    result = analysis['result']
    
    # Generate PDF
    try:
        from app.pdf_generator import generate_pdf_report
        pdf_content = generate_pdf_report(result, analysis_id)
        
        return FileResponse(
            pdf_content,
            media_type="application/pdf",
            filename=f"ats_report_{analysis_id}.pdf"
        )
    except ImportError:
        raise HTTPException(
            status_code=501,
            detail="PDF generation not available. Install reportlab or weasyprint."
        )


@app.get("/api/admin/weights")
async def get_default_weights():
    """Get default scoring weights."""
    engine = ScoringEngine()
    return {"weights": engine._default_weights()}


@app.post("/api/admin/settings")
async def save_settings(settings: AnalysisSettings):
    """Save custom analysis settings (for future database persistence)."""
    # In a real app, this would save to database
    return {
        "message": "Settings saved",
        "settings": settings.dict()
    }


def _generate_markdown_report(result: Dict) -> str:
    """Generate markdown report from analysis result."""
    
    md = f"""# ATS Resume Match Analysis Report

## Overall Score: {result['overall_score']}/100 - {result['label'].replace('_', ' ')}

---

## Category Breakdown

"""
    
    categories_display = {
        'keyword_skills': 'A) Keyword & Skills Match',
        'experience_relevance': 'B) Experience Relevance Match',
        'role_match': 'C) Role/Title Match',
        'seniority_match': 'D) Seniority/Years Match',
        'education_match': 'E) Education/Certs Match',
        'tooling_stack_match': 'F) Tooling/Stack Match',
        'recency_match': 'G) Recency Match',
        'red_flags': 'H) Red Flag Detection'
    }
    
    for key, display_name in categories_display.items():
        category = result['categories'][key]
        md += f"""### {display_name}: {category['score']}/100

"""
        if category['evidence']:
            for evidence in category['evidence']:
                md += f"- {evidence}\n"
        md += "\n"
    
    # Must-haves and nice-to-haves
    md += "## Keyword Matching\n\n"
    
    md += "### Must-Have Keywords\n"
    matched = sum(1 for kw in result['must_have'] if kw['matched'])
    total = len(result['must_have'])
    md += f"**Matched: {matched}/{total}**\n\n"
    
    for kw in result['must_have']:
        status = "✓" if kw['matched'] else "✗"
        md += f"- {status} {kw['term']}\n"
    
    md += "\n### Nice-to-Have Keywords\n"
    matched_nice = sum(1 for kw in result['nice_to_have'] if kw['matched'])
    total_nice = len(result['nice_to_have'])
    md += f"**Matched: {matched_nice}/{total_nice}**\n\n"
    
    for kw in result['nice_to_have']:
        status = "✓" if kw['matched'] else "✗"
        md += f"- {status} {kw['term']}\n"
    
    # Red flags
    if result['red_flags']:
        md += "\n## Red Flags\n\n"
        for flag in result['red_flags']:
            md += f"- ⚠️ {flag}\n"
    
    # Actions
    md += "\n## Recommendations\n\n"
    
    if result['actions']['good_fit_summary']:
        md += "### Good Fit\n"
        for item in result['actions']['good_fit_summary']:
            md += f"- ✓ {item}\n"
    
    if result['actions']['gaps']:
        md += "\n### Gaps to Address\n"
        for item in result['actions']['gaps']:
            md += f"- {item}\n"
    
    if result['actions']['resume_tailoring_suggestions']:
        md += "\n### Resume Tailoring Suggestions\n"
        for item in result['actions']['resume_tailoring_suggestions']:
            md += f"- {item}\n"
    
    if result['actions']['ats_keywords_to_add']:
        md += "\n### ATS Keywords to Consider Adding\n"
        md += f"{', '.join(result['actions']['ats_keywords_to_add'])}\n"
    
    # Metadata
    md += f"\n---\n\nGenerated: {result['metadata']['timestamp']}\n"
    md += f"Version: {result['metadata']['version']}\n"
    
    return md


# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("ATS Resume Match Analyzer API started")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("ATS Resume Match Analyzer API shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
