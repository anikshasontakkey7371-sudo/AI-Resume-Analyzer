"""
Report Generator Service.
Generates styled, professional PDF reports using ReportLab.
"""
import io
from datetime import datetime
from typing import Dict, Any

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class ReportGenerator:
    """Service to generate downloadable PDF reports."""

    @staticmethod
    def generate_pdf(analysis_data: Dict[str, Any]) -> io.BytesIO:
        """
        Builds a styled PDF evaluation report in memory and returns a BytesIO buffer.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        NAVY_PRIMARY = colors.HexColor("#0f172a")
        PURPLE_ACCENT = colors.HexColor("#6366f1")
        PURPLE_LIGHT = colors.HexColor("#ede9fe")
        TEXT_DARK = colors.HexColor("#1e293b")
        TEXT_MUTED = colors.HexColor("#64748b")
        CARD_BG = colors.HexColor("#f8fafc")

        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=24,
            textColor=NAVY_PRIMARY,
            spaceAfter=4
        )

        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=TEXT_MUTED,
            spaceAfter=12
        )

        section_heading = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=16,
            textColor=PURPLE_ACCENT,
            spaceBefore=10,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            'DocBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=TEXT_DARK
        )

        body_bold = ParagraphStyle(
            'DocBodyBold',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=13,
            textColor=TEXT_DARK
        )

        bullet_style = ParagraphStyle(
            'DocBullet',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=TEXT_DARK,
            leftIndent=12,
            firstLineIndent=-12
        )

        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=8,
            leading=11,
            textColor=TEXT_MUTED
        )

        elements = []

        # 1. Header
        role_title = analysis_data.get("target_role") or "Target Position"
        elements.append(Paragraph("AI RESUME ANALYZER", title_style))
        report_date = datetime.now().strftime("%B %d, %Y - %H:%M")
        mode_text = analysis_data.get("analysis_mode", "Automated Evaluation")
        elements.append(Paragraph(f"Analysis Report for <b>{role_title}</b> | Generated on {report_date} | {mode_text}", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=PURPLE_ACCENT, spaceAfter=10))

        # 2. Executive Summary Box
        summary_text = analysis_data.get("summary", "Analysis completed successfully.")
        summary_p = Paragraph(f"<b>Executive Summary:</b> {summary_text}", body_style)
        summary_table = Table([[summary_p]], colWidths=[540])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), PURPLE_LIGHT),
            ('PADDING', (0,0), (-1,-1), 8),
            ('BOX', (0,0), (-1,-1), 0.5, PURPLE_ACCENT),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 10))

        # 3. Score Grid
        scores = analysis_data.get("scores", {})
        overall = scores.get("overall", 0)
        skills = scores.get("skills_match", 0)
        exp = scores.get("experience_relevance", 0)
        kw = scores.get("keyword_coverage", 0)
        fmt = scores.get("formatting_readability", 0)

        score_data = [
            [
                Paragraph(f"<font size=16 color='{PURPLE_ACCENT.hexval()}'><b>{overall}/100</b></font><br/><font size=8 color='#64748b'>Overall Match</font>", body_style),
                Paragraph(f"<font size=14 color='#0f172a'><b>{skills}%</b></font><br/><font size=8 color='#64748b'>Skills Match (40%)</font>", body_style),
                Paragraph(f"<font size=14 color='#0f172a'><b>{exp}%</b></font><br/><font size=8 color='#64748b'>Experience (25%)</font>", body_style),
                Paragraph(f"<font size=14 color='#0f172a'><b>{kw}%</b></font><br/><font size=8 color='#64748b'>Keywords (20%)</font>", body_style),
                Paragraph(f"<font size=14 color='#0f172a'><b>{fmt}%</b></font><br/><font size=8 color='#64748b'>Formatting (15%)</font>", body_style),
            ]
        ]
        score_table = Table(score_data, colWidths=[110, 107, 107, 107, 107])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        elements.append(score_table)
        elements.append(Spacer(1, 8))

        # 4. Skills Assessment Table
        elements.append(Paragraph("Skills Assessment", section_heading))
        matched_skills = analysis_data.get("skills_matched", [])
        missing_skills = analysis_data.get("skills_missing", [])
        
        matched_str = ", ".join(matched_skills) if matched_skills else "None explicitly detected"
        missing_str = ", ".join(missing_skills) if missing_skills else "No critical skills missing"
        
        skills_table_data = [
            [
                Paragraph("<font color='#047857'><b>Matched Skills:</b></font>", body_bold),
                Paragraph(matched_str, body_style)
            ],
            [
                Paragraph("<font color='#b91c1c'><b>Missing Skills:</b></font>", body_bold),
                Paragraph(missing_str, body_style)
            ]
        ]
        skills_table = Table(skills_table_data, colWidths=[120, 420])
        skills_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('PADDING', (0,0), (-1,-1), 6),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        elements.append(skills_table)
        elements.append(Spacer(1, 8))

        # 5. Strengths & Improvements
        elements.append(Paragraph("Strengths & Areas for Improvement", section_heading))
        strengths = analysis_data.get("strengths", [])
        improvements = analysis_data.get("improvements", [])

        for s in strengths[:3]:
            elements.append(Paragraph(f"+ <b>Strength:</b> {s}", bullet_style))
        elements.append(Spacer(1, 4))
        for imp in improvements[:3]:
            elements.append(Paragraph(f"! <b>Opportunity:</b> {imp}", bullet_style))
        elements.append(Spacer(1, 8))

        # 6. STAR Bullet Point Rewrites
        bullet_suggs = analysis_data.get("bullet_point_suggestions", [])
        if bullet_suggs:
            elements.append(Paragraph("High-Impact Bullet Point Rewrites (STAR Method)", section_heading))
            for b in bullet_suggs[:2]:
                b_data = [
                    [Paragraph("<b>Original:</b>", body_bold), Paragraph(f"<i>\"{b.get('original', '')}\"</i>", body_style)],
                    [Paragraph("<font color='#4f46e5'><b>Improved:</b></font>", body_bold), Paragraph(f"<b>{b.get('improved', '')}</b>", body_style)],
                    [Paragraph("<b>Reason:</b>", body_bold), Paragraph(b.get('reason', ''), body_style)]
                ]
                b_table = Table(b_data, colWidths=[70, 470])
                b_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#fbfbfe")),
                    ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
                    ('PADDING', (0,0), (-1,-1), 4),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ]))
                elements.append(b_table)
                elements.append(Spacer(1, 4))

        # 7. Recommended Skills Roadmap
        rec_skills = analysis_data.get("recommended_skills_to_learn", [])
        if rec_skills:
            elements.append(Paragraph("Recommended Skills Roadmap", section_heading))
            for item in rec_skills[:3]:
                elements.append(Paragraph(f"• <b>{item.get('skill')}:</b> [{item.get('priority', 'Medium')} Priority] {item.get('suggestion')}", bullet_style))
            elements.append(Spacer(1, 8))

        # 8. Transparency Note
        criteria = analysis_data.get("transparent_criteria", {})
        disclaimer = criteria.get("disclaimer", "This score is an estimate and does not guarantee ATS selection.")
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceBefore=6, spaceAfter=6))
        elements.append(Paragraph(f"<b>Transparency Note:</b> Overall Score is calculated as 40% Skills + 25% Experience + 20% Keywords + 15% Formatting. {disclaimer}", disclaimer_style))

        doc.build(elements)
        buffer.seek(0)
        return buffer
