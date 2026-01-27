"""
PDF report generator for analysis results.
"""

import io
from typing import Dict, BinaryIO
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def generate_pdf_report(result: Dict, analysis_id: str) -> BinaryIO:
    """
    Generate PDF report from analysis result.
    Uses reportlab for PDF generation.
    """
    
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    except ImportError:
        logger.error("reportlab not installed")
        raise ImportError("PDF generation requires reportlab. Install with: pip install reportlab")
    
    # Create PDF document in memory
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    
    # Container for PDF elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    title = Paragraph("ATS Resume Match Analysis Report", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))
    
    # Overall Score
    score = result['overall_score']
    label = result['label'].replace('_', ' ')
    
    # Color code by label
    if score >= 75:
        score_color = colors.HexColor('#28a745')  # Green
    elif score >= 50:
        score_color = colors.HexColor('#ffc107')  # Yellow
    else:
        score_color = colors.HexColor('#dc3545')  # Red
    
    score_style = ParagraphStyle(
        'ScoreStyle',
        parent=styles['Normal'],
        fontSize=36,
        textColor=score_color,
        alignment=TA_CENTER,
        spaceAfter=6
    )
    
    label_style = ParagraphStyle(
        'LabelStyle',
        parent=styles['Normal'],
        fontSize=16,
        textColor=score_color,
        alignment=TA_CENTER,
        spaceAfter=24
    )
    
    score_paragraph = Paragraph(f"{score}/100", score_style)
    label_paragraph = Paragraph(label, label_style)
    
    elements.append(score_paragraph)
    elements.append(label_paragraph)
    elements.append(Spacer(1, 0.2*inch))
    
    # Category Breakdown
    elements.append(Paragraph("Category Breakdown", heading_style))
    
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
    
    category_data = [['Category', 'Score']]
    for key, display_name in categories_display.items():
        if key in result['categories']:
            score_val = result['categories'][key]['score']
            category_data.append([display_name, f"{score_val:.1f}"])
    
    category_table = Table(category_data, colWidths=[4*inch, 1*inch])
    category_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#333333')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
    ]))
    
    elements.append(category_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Keyword Matching
    elements.append(Paragraph("Keyword Matching", heading_style))
    
    must_haves = result['must_have']
    matched_must = sum(1 for kw in must_haves if kw['matched'])
    total_must = len(must_haves)
    
    nice_to_haves = result['nice_to_have']
    matched_nice = sum(1 for kw in nice_to_haves if kw['matched'])
    total_nice = len(nice_to_haves)
    
    keyword_data = [
        ['Type', 'Matched', 'Total', 'Match %'],
        ['Must-Have', matched_must, total_must, f"{(matched_must/total_must*100):.0f}%" if total_must > 0 else "N/A"],
        ['Nice-to-Have', matched_nice, total_nice, f"{(matched_nice/total_nice*100):.0f}%" if total_nice > 0 else "N/A"]
    ]
    
    keyword_table = Table(keyword_data, colWidths=[2*inch, 1.2*inch, 1*inch, 1*inch])
    keyword_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#333333')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
    ]))
    
    elements.append(keyword_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Red Flags
    if result['red_flags']:
        elements.append(Paragraph("Red Flags", heading_style))
        
        for flag in result['red_flags']:
            flag_text = Paragraph(f"⚠️ {flag}", styles['Normal'])
            elements.append(flag_text)
        
        elements.append(Spacer(1, 0.3*inch))
    
    # Recommendations
    actions = result['actions']
    
    if actions['good_fit_summary']:
        elements.append(Paragraph("Strengths", heading_style))
        for item in actions['good_fit_summary']:
            elements.append(Paragraph(f"✓ {item}", styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
    
    if actions['gaps']:
        elements.append(Paragraph("Gaps to Address", heading_style))
        for item in actions['gaps']:
            elements.append(Paragraph(f"• {item}", styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
    
    if actions['resume_tailoring_suggestions']:
        elements.append(Paragraph("Tailoring Suggestions", heading_style))
        for item in actions['resume_tailoring_suggestions']:
            elements.append(Paragraph(f"• {item}", styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
    
    if actions['ats_keywords_to_add']:
        elements.append(Paragraph("Keywords to Consider Adding", heading_style))
        keywords_text = ", ".join(actions['ats_keywords_to_add'])
        elements.append(Paragraph(keywords_text, styles['Normal']))
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("_" * 80, styles['Normal']))
    
    footer_text = f"""
    <b>Analysis ID:</b> {analysis_id}<br/>
    <b>Generated:</b> {result['metadata']['timestamp']}<br/>
    <b>Version:</b> {result['metadata']['version']}<br/>
    <b>Disclaimer:</b> This analysis is based on keyword matching and heuristic scoring.
    It should be used as a tool to assist in hiring decisions, not as the sole criterion.
    """
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_LEFT,
        spaceAfter=12
    )
    
    elements.append(Paragraph(footer_text, footer_style))
    
    # Build PDF
    doc.build(elements)
    
    # Return buffer for file response
    pdf_buffer.seek(0)
    return pdf_buffer
