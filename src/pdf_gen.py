"""
pdf_gen.py
Generates professional PDF documents from product content.
Uses reportlab — completely free, no external API needed.
"""
import io
from pathlib import Path


def generate_pdf(product: dict, output_path: str) -> str:
    """
    Generate a professional PDF from product content dict.
    Returns the path to the generated PDF.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.colors import HexColor, white, black
        from reportlab.lib.units import cm
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                         HRFlowable, Table, TableStyle)
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    except ImportError:
        raise RuntimeError("reportlab not installed. Run: pip install reportlab")

    # Colors
    PRIMARY   = HexColor('#2E4057')   # Dark blue
    ACCENT    = HexColor('#048A81')   # Teal
    LIGHT_BG  = HexColor('#F0F4F8')   # Light gray-blue
    TEXT      = HexColor('#2D3748')   # Dark gray

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'Title', parent=styles['Title'],
        fontSize=20, textColor=white,
        spaceAfter=6, alignment=TA_CENTER,
        fontName='Helvetica-Bold',
    )
    heading_style = ParagraphStyle(
        'Heading', parent=styles['Heading2'],
        fontSize=13, textColor=PRIMARY,
        spaceBefore=14, spaceAfter=6,
        fontName='Helvetica-Bold',
    )
    body_style = ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontSize=10, textColor=TEXT,
        spaceAfter=8, leading=16,
        fontName='Helvetica',
        alignment=TA_JUSTIFY,
    )
    disclaimer_style = ParagraphStyle(
        'Disclaimer', parent=styles['Normal'],
        fontSize=8, textColor=HexColor('#718096'),
        spaceAfter=4, fontName='Helvetica-Oblique',
        alignment=TA_CENTER,
    )

    story = []

    # ── Title block ──────────────────────────────────────────────────────────
    title_data = [[Paragraph(product['title'], title_style)]]
    title_table = Table(title_data, colWidths=[17*cm])
    title_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), PRIMARY),
        ('ROUNDEDCORNERS', [8]),
        ('TOPPADDING', (0,0), (-1,-1), 16),
        ('BOTTOMPADDING', (0,0), (-1,-1), 16),
        ('LEFTPADDING', (0,0), (-1,-1), 20),
        ('RIGHTPADDING', (0,0), (-1,-1), 20),
    ]))
    story.append(title_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Subtitle / category ───────────────────────────────────────────────────
    cat_readable = product['category'].replace('_', ' ').title()
    story.append(Paragraph(
        f"<font color='#718096' size='9'>{cat_readable} | Professional Digital Guide</font>",
        ParagraphStyle('Sub', parent=styles['Normal'], alignment=TA_CENTER,
                       fontName='Helvetica', spaceAfter=4)
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=12))

    # ── Sections ─────────────────────────────────────────────────────────────
    for heading, content in product['sections']:
        story.append(Paragraph(heading, heading_style))
        story.append(HRFlowable(width="40%", thickness=1, color=ACCENT, spaceAfter=6))

        # Handle multi-line content
        for line in content.split('\n'):
            line = line.strip()
            if line:
                if line.startswith('•') or line.startswith('✓') or line.startswith('✗'):
                    story.append(Paragraph(
                        f"&nbsp;&nbsp;&nbsp;{line}",
                        ParagraphStyle('Bullet', parent=body_style,
                                      leftIndent=12, spaceAfter=4)
                    ))
                else:
                    story.append(Paragraph(line, body_style))
            else:
                story.append(Spacer(1, 0.2*cm))

        story.append(Spacer(1, 0.3*cm))

    # ── Footer disclaimer ─────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#CBD5E0'),
                            spaceBefore=12, spaceAfter=8))
    story.append(Paragraph(
        "This guide is for educational purposes only and does not constitute medical advice. "
        "Always consult a qualified healthcare professional for diagnosis and treatment.",
        disclaimer_style
    ))
    story.append(Paragraph(
        "© 2026 MedEd Digital Products | All Rights Reserved | Instant Digital Download",
        disclaimer_style
    ))

    doc.build(story)
    size_kb = Path(output_path).stat().st_size // 1024
    print(f"  [pdf] Generated: {output_path} ({size_kb} KB)")
    return output_path
