"""
DeepFake Shield - PDF Report Generator
Clean, professional, concise reports with user input and logo.
"""

import io
import os
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, Image as RLImage
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("ReportLab not available. PDF reports disabled.")

try:
    from PIL import Image as PILImage
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def _create_logo_image():
    """Create a simple shield logo using ReportLab drawing or return None."""
    try:
        from reportlab.graphics.shapes import Drawing, Circle, String, Polygon
        from reportlab.graphics import renderPDF
        from reportlab.lib.colors import HexColor

        d = Drawing(50, 50)

        # Shield shape as polygon
        shield_points = [25, 5, 45, 15, 42, 35, 25, 48, 8, 35, 5, 15]
        shield = Polygon(shield_points,
                        fillColor=HexColor('#667eea'),
                        strokeColor=HexColor('#764ba2'),
                        strokeWidth=1.5)
        d.add(shield)

        # Checkmark
        check = String(15, 20, '✓',
                       fontSize=20,
                       fillColor=colors.white,
                       fontName='Helvetica-Bold')
        d.add(check)

        return d
    except Exception:
        return None


def generate_pdf_report(scan_result):
    """Generate a professional, concise PDF report with user input."""
    if not REPORTLAB_AVAILABLE:
        logger.warning("Cannot generate PDF: ReportLab not installed.")
        return None

    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=25 * mm,
            leftMargin=25 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
        )

        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'ReportTitle', parent=styles['Title'],
            fontSize=24, spaceAfter=4,
            textColor=colors.HexColor('#1a1a2e'),
            fontName='Helvetica-Bold', alignment=TA_CENTER,
        )
        subtitle_style = ParagraphStyle(
            'ReportSubtitle', parent=styles['Normal'],
            fontSize=11, spaceAfter=16,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
        )
        heading_style = ParagraphStyle(
            'SectionHeading', parent=styles['Heading2'],
            fontSize=13, spaceBefore=14, spaceAfter=6,
            textColor=colors.HexColor('#16213e'),
            fontName='Helvetica-Bold',
        )
        body_style = ParagraphStyle(
            'BodyText', parent=styles['Normal'],
            fontSize=10, spaceAfter=6, leading=14,
            alignment=TA_LEFT,
        )
        small_style = ParagraphStyle(
            'SmallText', parent=styles['Normal'],
            fontSize=8, textColor=colors.HexColor('#999999'),
            alignment=TA_CENTER, spaceBefore=6,
        )

        elements = []

        # ── Header with Logo ──
        logo_drawing = _create_logo_image()

        header_data = []
        if logo_drawing:
            header_data = [[
                logo_drawing,
                Paragraph(
                    '<font size="20" color="#1a1a2e"><b>DeepFake Shield</b></font>'
                    '<br/><font size="9" color="#718096">Media Authenticity Verification Report</font>',
                    ParagraphStyle('HeaderText', parent=styles['Normal'], alignment=TA_LEFT, leading=22)
                ),
                Paragraph(
                    f'<font size="8" color="#999999">Report ID: {str(scan_result.id)[:8]}</font>'
                    f'<br/><font size="8" color="#999999">{scan_result.created_at.strftime("%Y-%m-%d %H:%M UTC")}</font>',
                    ParagraphStyle('HeaderRight', parent=styles['Normal'], alignment=TA_RIGHT, leading=12)
                )
            ]]
            header_table = Table(header_data, colWidths=[60, 300, 110])
        else:
            header_data = [[
                Paragraph(
                    '<font size="20" color="#1a1a2e"><b>🛡️ DeepFake Shield</b></font>'
                    '<br/><font size="9" color="#718096">Media Authenticity Verification Report</font>',
                    ParagraphStyle('HeaderText', parent=styles['Normal'], alignment=TA_LEFT, leading=22)
                ),
                Paragraph(
                    f'<font size="8" color="#999999">ID: {str(scan_result.id)[:8]}</font>'
                    f'<br/><font size="8" color="#999999">{scan_result.created_at.strftime("%Y-%m-%d %H:%M")}</font>',
                    ParagraphStyle('HeaderRight', parent=styles['Normal'], alignment=TA_RIGHT, leading=12)
                )
            ]]
            header_table = Table(header_data, colWidths=[360, 110])

        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(header_table)
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#667eea')))
        elements.append(Spacer(1, 12))

        # ── Score Section ──
        score = scan_result.authenticity_score
        if score >= 75:
            score_color = '#28a745'
            score_bg = '#d4edda'
        elif score >= 40:
            score_color = '#e67e22'
            score_bg = '#fff3cd'
        else:
            score_color = '#dc3545'
            score_bg = '#f8d7da'

        score_data = [[
            Paragraph(
                f'<font size="36" color="{score_color}"><b>{score:.1f}%</b></font>',
                ParagraphStyle('ScoreNum', parent=styles['Normal'], alignment=TA_CENTER)
            ),
            Paragraph(
                f'<font size="14" color="{score_color}"><b>{scan_result.score_label}</b></font>'
                f'<br/><br/><font size="10" color="#555555">{scan_result.real_vs_fake}</font>'
                f'<br/><font size="9" color="#888888">Scan Type: {scan_result.scan_type.upper()}</font>'
                f'<br/><font size="9" color="#888888">File: {scan_result.original_filename or "Text Input"}</font>'
                f'<br/><font size="9" color="#888888">Analyst: {scan_result.user.username}</font>',
                ParagraphStyle('ScoreInfo', parent=styles['Normal'], alignment=TA_LEFT, leading=15)
            ),
        ]]
        score_table = Table(score_data, colWidths=[140, 330])
        score_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(score_bg)),
            ('ROUNDEDCORNERS', [8, 8, 8, 8]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(score_table)
        elements.append(Spacer(1, 14))

        # ── User Input Section ──
        if scan_result.scan_type == 'text' and scan_result.submitted_text:
            elements.append(Paragraph("Submitted Text", heading_style))
            # Truncate for report
            display_text = scan_result.submitted_text[:800]
            if len(scan_result.submitted_text) > 800:
                display_text += '... [truncated]'
            elements.append(Paragraph(
                f'<font size="9" color="#444444"><i>"{display_text}"</i></font>',
                ParagraphStyle('QuoteText', parent=body_style,
                              backColor=colors.HexColor('#f8f9fa'),
                              borderPadding=8, leading=13)
            ))
            elements.append(Spacer(1, 8))

        elif scan_result.scan_type == 'image' and scan_result.uploaded_file:
            elements.append(Paragraph("Analyzed Image", heading_style))
            try:
                img_path = scan_result.processed_file.path if scan_result.processed_file else scan_result.uploaded_file.path
                if os.path.exists(img_path):
                    img = RLImage(img_path)
                    # Scale to fit page width
                    max_w = 460
                    max_h = 250
                    iw, ih = img.drawWidth, img.drawHeight
                    if PIL_AVAILABLE:
                        pil_img = PILImage.open(img_path)
                        iw, ih = pil_img.size
                    ratio = min(max_w / iw, max_h / ih)
                    img.drawWidth = iw * ratio
                    img.drawHeight = ih * ratio
                    img.hAlign = 'CENTER'
                    elements.append(img)
                    elements.append(Spacer(1, 8))
            except Exception as e:
                logger.debug(f"Could not embed image in PDF: {e}")

        # ── Analysis Summary (Concise) ──
        if scan_result.explanation:
            elements.append(Paragraph("Analysis Summary", heading_style))
            # Keep it concise — first 300 chars
            explanation = scan_result.explanation[:400]
            if len(scan_result.explanation) > 400:
                explanation += '...'
            elements.append(Paragraph(explanation, body_style))
            elements.append(Spacer(1, 6))

        # ── Key Metrics Table ──
        detailed = scan_result.detailed_results
        if detailed and isinstance(detailed, dict):
            elements.append(Paragraph("Key Metrics", heading_style))

            # Filter and format key metrics only
            skip_keys = {
                'face_boxes', 'exif_data', 'frame_scores', 'screenshot_reasons',
                'processed_image_bytes', 'filename', 'scene_description',
                'analysis_summary', 'description', 'explanation', 'summary',
                'real_vs_fake', 'classification', 'authenticity_score',
                'image_dimensions', 'deep_features_available',
                'top_class_confidence', 'prediction_entropy',
            }

            # Get detailed_metrics if nested
            metrics_source = detailed.get('detailed_metrics', detailed)
            if not isinstance(metrics_source, dict):
                metrics_source = detailed

            metrics_data = [['Metric', 'Value']]
            count = 0

            for key, value in metrics_source.items():
                if key in skip_keys:
                    continue
                if isinstance(value, (dict, list)):
                    continue
                if count >= 16:  # Limit to 16 key metrics
                    break

                display_key = key.replace('_', ' ').title()
                if isinstance(value, float):
                    if value < 1 and value > 0:
                        display_value = f"{value:.4f}"
                    else:
                        display_value = f"{value:.2f}"
                elif isinstance(value, bool):
                    display_value = "Yes" if value else "No"
                else:
                    display_value = str(value)[:50]

                metrics_data.append([display_key, display_value])
                count += 1

            if len(metrics_data) > 1:
                metrics_table = Table(metrics_data, colWidths=[240, 230])
                metrics_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16213e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1),
                     [colors.white, colors.HexColor('#f8f9fa')]),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 1), (0, -1), 'Helvetica'),
                    ('FONTNAME', (1, 1), (1, -1), 'Courier'),
                ]))
                elements.append(metrics_table)

        # ── Score Legend ──
        elements.append(Spacer(1, 16))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#dddddd')))
        elements.append(Spacer(1, 8))

        legend_data = [
            ['Score', 'Classification'],
            ['0 – 39', 'Likely Fake / Synthetic'],
            ['40 – 74', 'Suspicious / Inconclusive'],
            ['75 – 99', 'Likely Real / Authentic'],
            ['100', 'Highly Authentic'],
        ]
        legend_table = Table(legend_data, colWidths=[80, 390])
        legend_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f2f5')),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#e0e0e0')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#666666')),
        ]))
        elements.append(legend_table)

        # ── Footer ──
        elements.append(Spacer(1, 16))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e0e0e0')))
        elements.append(Paragraph(
            f"Generated by DeepFake Shield v1.0.0 | "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
            f"deepfakeshield.com",
            small_style
        ))
        elements.append(Paragraph(
            "This report uses hybrid AI analysis. Results are informational and may not be definitive.",
            small_style
        ))

        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        logger.info(f"PDF report generated: {len(pdf_bytes)} bytes")
        return pdf_bytes

    except Exception as e:
        logger.error(f"PDF generation failed: {e}", exc_info=True)
        return None