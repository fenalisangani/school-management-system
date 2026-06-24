"""Generate polished tabular PDF reports with ReportLab."""

from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

BRAND_PRIMARY = colors.HexColor('#4f46e5')
BRAND_PRIMARY_DARK = colors.HexColor('#312e81')
BRAND_SUCCESS = colors.HexColor('#059669')
BRAND_SUCCESS_BG = colors.HexColor('#ecfdf5')
BRAND_DANGER = colors.HexColor('#dc2626')
BRAND_DANGER_BG = colors.HexColor('#fef2f2')
BRAND_WARNING = colors.HexColor('#d97706')
BRAND_WARNING_BG = colors.HexColor('#fffbeb')
BRAND_MUTED = colors.HexColor('#64748b')
BRAND_BORDER = colors.HexColor('#e2e8f0')
BRAND_SURFACE = colors.HexColor('#f8fafc')

LOGO_PATH = Path(settings.BASE_DIR) / 'static' / 'img' / 'pdf_logo.png'
INSTITUTION_NAME = 'School Management System'
INSTITUTION_TAGLINE = 'School & College ERP · Fees in INR · Attendance & Reports'


def pdf_inr(amount):
    """INR formatting safe for PDF fonts (Rs. instead of ₹)."""
    from fees.currency import format_inr

    return format_inr(amount, symbol='Rs.')


def _styles():
    base = getSampleStyleSheet()
    return {
        'brand': ParagraphStyle(
            'Brand',
            parent=base['Normal'],
            fontSize=8,
            leading=10,
            textColor=BRAND_MUTED,
            spaceAfter=0,
        ),
        'institution': ParagraphStyle(
            'Institution',
            parent=base['Heading2'],
            fontSize=13,
            leading=15,
            textColor=BRAND_PRIMARY_DARK,
            spaceAfter=2,
        ),
        'title': ParagraphStyle(
            'ReportTitle',
            parent=base['Heading1'],
            fontSize=18,
            leading=22,
            textColor=BRAND_PRIMARY_DARK,
            spaceBefore=4,
            spaceAfter=8,
        ),
        'meta': ParagraphStyle(
            'ReportMeta',
            parent=base['Normal'],
            fontSize=9,
            leading=12,
            textColor=BRAND_MUTED,
            spaceAfter=2,
        ),
        'summary_value': ParagraphStyle(
            'SummaryValue',
            parent=base['Normal'],
            fontSize=14,
            leading=16,
            textColor=BRAND_PRIMARY_DARK,
            alignment=TA_CENTER,
        ),
        'summary_label': ParagraphStyle(
            'SummaryLabel',
            parent=base['Normal'],
            fontSize=8,
            leading=10,
            textColor=BRAND_MUTED,
            alignment=TA_CENTER,
        ),
        'footer': ParagraphStyle(
            'Footer',
            parent=base['Normal'],
            fontSize=8,
            textColor=BRAND_MUTED,
        ),
        'signature': ParagraphStyle(
            'Signature',
            parent=base['Normal'],
            fontSize=9,
            textColor=BRAND_MUTED,
            spaceBefore=6,
        ),
        'status_ok': ParagraphStyle(
            'StatusOk',
            parent=base['Normal'],
            fontSize=9,
            textColor=BRAND_SUCCESS,
        ),
        'status_bad': ParagraphStyle(
            'StatusBad',
            parent=base['Normal'],
            fontSize=9,
            textColor=BRAND_DANGER,
        ),
    }


def _letterhead(title, styles):
    story = []
    logo = LOGO_PATH if LOGO_PATH.exists() else None
    left = Image(str(logo), width=16 * mm, height=16 * mm) if logo else ''
    header_data = [[
        left,
        Paragraph(
            f'<b>{INSTITUTION_NAME}</b><br/>'
            f'<font size="8" color="#64748b">{INSTITUTION_TAGLINE}</font>',
            styles['institution'],
        ),
    ]]
    header_table = Table(header_data, colWidths=[18 * mm, None])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width='100%', thickness=2, color=BRAND_PRIMARY, spaceAfter=8))
    story.append(Paragraph(title, styles['title']))
    return story


def _summary_cards(stats, styles, doc_width):
    """stats: list of {label, value, tone?}."""
    if not stats:
        return []
    tones = {
        'default': (BRAND_SURFACE, BRAND_PRIMARY_DARK),
        'success': (BRAND_SUCCESS_BG, BRAND_SUCCESS),
        'warning': (BRAND_WARNING_BG, BRAND_WARNING),
        'danger': (BRAND_DANGER_BG, BRAND_DANGER),
    }
    cells = []
    col_width = doc_width / len(stats)
    table_data = []
    row_labels = []
    row_values = []
    for item in stats:
        bg, fg = tones.get(item.get('tone', 'default'), tones['default'])
        row_values.append(Paragraph(f'<b>{item["value"]}</b>', styles['summary_value']))
        row_labels.append(Paragraph(item['label'], styles['summary_label']))
    table_data = [row_values, row_labels]
    table = Table(table_data, colWidths=[col_width] * len(stats))
    style_cmds = [
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 0.5, BRAND_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BRAND_BORDER),
    ]
    for i, item in enumerate(stats):
        bg, _ = tones.get(item.get('tone', 'default'), tones['default'])
        style_cmds.append(('BACKGROUND', (i, 0), (i, 1), bg))
    table.setStyle(TableStyle(style_cmds))
    return [table, Spacer(1, 10)]


def _format_cell(value, col_index, status_col, row_status, styles):
    if status_col is not None and col_index == status_col and row_status:
        if row_status == 'ok':
            return Paragraph(f'<b>{value}</b>', styles['status_ok'])
        if row_status == 'bad':
            return Paragraph(f'<b>{value}</b>', styles['status_bad'])
    return value


def _draw_page_frame(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(BRAND_BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(doc.leftMargin, 14 * mm, A4[0] - doc.rightMargin, 14 * mm)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(BRAND_MUTED)
    generated = timezone.localtime().strftime('%d %b %Y, %I:%M %p IST')
    canvas.drawString(doc.leftMargin, 10 * mm, f'{INSTITUTION_NAME} · Generated {generated}')
    canvas.drawRightString(A4[0] - doc.rightMargin, 10 * mm, f'Page {canvas.getPageNumber()}')
    canvas.restoreState()


def build_report_pdf(
    *,
    title,
    filename,
    meta_lines,
    headers,
    rows,
    summary_stats=None,
    row_statuses=None,
    status_col=None,
):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=14 * mm,
        bottomMargin=18 * mm,
        title=title,
    )
    styles = _styles()
    story = _letterhead(title, styles)
    for line in meta_lines:
        story.append(Paragraph(line, styles['meta']))
    story.append(Spacer(1, 6))
    story.extend(_summary_cards(summary_stats or [], styles, doc.width))

    table_data = [headers]
    if rows:
        for row_index, row in enumerate(rows):
            status = (row_statuses or [None] * len(rows))[row_index]
            table_data.append([
                _format_cell(cell, col_index, status_col, status, styles)
                for col_index, cell in enumerate(row)
            ])
    else:
        table_data.append(['No records for this period.'] + [''] * (len(headers) - 1))

    col_count = len(headers)
    col_width = doc.width / col_count
    if col_count == 5:
        col_widths = [doc.width * 0.32, doc.width * 0.12, doc.width * 0.12, doc.width * 0.16, doc.width * 0.28]
    elif col_count == 6:
        col_widths = [doc.width * 0.16, doc.width * 0.22, doc.width * 0.16, doc.width * 0.14, doc.width * 0.12, doc.width * 0.20]
    else:
        col_widths = [col_width] * col_count

    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.25, BRAND_BORDER),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BRAND_SURFACE]),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 16))
    story.append(HRFlowable(width='40%', thickness=0.5, color=BRAND_BORDER, hAlign='LEFT'))
    story.append(Paragraph(
        '<b>Prepared by</b> ___________________________ &nbsp;&nbsp;&nbsp; '
        '<b>Verified by</b> ___________________________',
        styles['signature'],
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        'This is a computer-generated report from the School Management System.',
        styles['footer'],
    ))

    doc.build(story, onFirstPage=_draw_page_frame, onLaterPages=_draw_page_frame)
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
