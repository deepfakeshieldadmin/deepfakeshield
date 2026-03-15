import os
from datetime import datetime
from django.conf import settings

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    )
    from reportlab.lib.enums import TA_CENTER
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False


def generate_pdf_report(scan, results_dict):
    if not REPORTLAB_AVAILABLE:
        return None

    try:
        reports_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
        os.makedirs(reports_dir, exist_ok=True)

        filename = f"report_{scan.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(reports_dir, filename)

        doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=40, bottomMargin=30, leftMargin=35, rightMargin=35)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=22,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=10,
        )
        sub_style = ParagraphStyle(
            'Sub',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#64748b'),
            spaceAfter=18,
        )
        heading_style = ParagraphStyle(
            'Head',
            parent=styles['Heading2'],
            fontSize=13,
            textColor=colors.HexColor('#0f172a'),
            spaceBefore=12,
            spaceAfter=8,
        )
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=10,
            leading=15,
            textColor=colors.HexColor('#334155'),
            spaceAfter=6,
        )

        elements = []
        elements.append(Paragraph("DeepFake Shield", title_style))
        elements.append(Paragraph("Media Authenticity Verification Report", sub_style))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#38bdf8')))
        elements.append(Spacer(1, 14))

        elements.append(Paragraph("Scan Information", heading_style))
        info = [
            ['Property', 'Value'],
            ['Scan Type', scan.scan_type.title()],
            ['File Name', scan.original_filename or 'N/A'],
            ['Authenticity Score', str(scan.authenticity_score)],
            ['Classification', scan.classification_display],
            ['Generated On', scan.created_at.strftime('%Y-%m-%d %H:%M:%S')],
        ]
        table = Table(info, colWidths=[170, 320])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#cbd5e1')),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(table)

        if scan.explanation:
            elements.append(Paragraph("Explanation", heading_style))
            elements.append(Paragraph(scan.explanation, body_style))

        if isinstance(results_dict, dict):
            summary = results_dict.get('analysis_summary')
            if summary:
                elements.append(Paragraph("Summary", heading_style))
                elements.append(Paragraph(summary, body_style))

            scene_description = results_dict.get('scene_description')
            if scene_description:
                elements.append(Paragraph("Description", heading_style))
                elements.append(Paragraph(scene_description, body_style))

            detail_rows = [['Metric', 'Value']]
            for key, value in results_dict.items():
                if key in ('exif_data', 'analysis_summary', 'description', 'scene_description', 'face_boxes'):
                    continue
                label = key.replace('_', ' ').title()
                detail_rows.append([label, str(value)])

            elements.append(Paragraph("Detailed Metrics", heading_style))
            detail_table = Table(detail_rows, colWidths=[200, 290])
            detail_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#334155')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#cbd5e1')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            elements.append(detail_table)

        elements.append(Spacer(1, 18))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1')))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(
            "This report is a practical AI-assisted authenticity estimate and should not be considered final forensic proof.",
            body_style
        ))

        doc.build(elements)
        return os.path.join('reports', filename)

    except Exception:
        return None