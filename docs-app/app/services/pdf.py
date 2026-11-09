from __future__ import annotations

import io
import logging
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.config import BASE_DIR
from app.services.amount_words import amount_in_words_eur
from app.textutil import nfc, vat_label

logger = logging.getLogger(__name__)

APP_DIR = BASE_DIR / "app"
TEMPLATES_DIR = APP_DIR / "templates"
FONTS_DIR = APP_DIR / "static" / "fonts"
FONT_REGULAR = FONTS_DIR / "DejaVuSans.ttf"
FONT_BOLD = FONTS_DIR / "DejaVuSans-Bold.ttf"
LEGAL_LINE = nfc("Dokuments sagatavots elektroniski un derīgs bez paraksta.")

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)
_env.globals["vat_label"] = vat_label
_env.globals["amount_words"] = amount_in_words_eur
_env.filters["nfc"] = nfc
_env.filters["amount_words"] = amount_in_words_eur

_WEASY_OK: bool | None = None
_REPORTLAB_FONTS_READY = False


def weasyprint_available() -> bool:
    global _WEASY_OK
    if _WEASY_OK is not None:
        return _WEASY_OK
    try:
        from weasyprint import HTML  # noqa: F401

        _WEASY_OK = True
    except Exception as exc:  # pragma: no cover - env dependent
        logger.warning("WeasyPrint unavailable, using ReportLab fallback: %s", exc)
        _WEASY_OK = False
    return _WEASY_OK


def _ensure_reportlab_fonts() -> str:
    """Register DejaVu Sans for ReportLab; return font family name."""
    global _REPORTLAB_FONTS_READY
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    if not _REPORTLAB_FONTS_READY:
        pdfmetrics.registerFont(TTFont("DejaVuSans", str(FONT_REGULAR)))
        pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", str(FONT_BOLD)))
        _REPORTLAB_FONTS_READY = True
    return "DejaVuSans"


def _nfc_doc_fields(document: Any) -> None:
    for attr in (
        "number",
        "seller_name",
        "seller_reg_nr",
        "seller_vat_nr",
        "seller_address",
        "seller_bank",
        "seller_iban",
        "seller_phone",
        "seller_email",
        "seller_logo_filename",
        "buyer_name",
        "buyer_reg_nr",
        "buyer_vat_nr",
        "buyer_address",
        "buyer_phone",
        "buyer_email",
        "notes",
        "currency",
    ):
        if hasattr(document, attr):
            setattr(document, attr, nfc(getattr(document, attr)))
    for line in getattr(document, "lines", []) or []:
        if hasattr(line, "description"):
            line.description = nfc(line.description)
        if hasattr(line, "unit"):
            line.unit = nfc(line.unit)


def render_document_html(document: Any) -> str:
    _nfc_doc_fields(document)
    template_name = (
        "pdf/invoice.html"
        if document.doc_type == "invoice"
        else "pdf/delivery_note.html"
    )
    template = _env.get_template(template_name)
    return template.render(
        doc=document,
        engine="weasyprint",
        vat_label=vat_label,
        amount_words=amount_in_words_eur,
    )


def html_to_pdf_weasy(html: str) -> bytes:
    from weasyprint import HTML

    # base_url = app/ so url("static/fonts/...") resolves
    return HTML(string=html, base_url=str(APP_DIR)).write_pdf()


def document_to_pdf_reportlab(document: Any) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    _nfc_doc_fields(document)
    font = _ensure_reportlab_fonts()
    font_bold = "DejaVuSans-Bold"

    buffer = io.BytesIO()
    doc_pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleLV",
        parent=styles["Heading1"],
        fontName=font_bold,
        fontSize=16,
        spaceAfter=6,
        alignment=2,  # right
    )
    normal = ParagraphStyle(
        "BodyLV", parent=styles["Normal"], fontName=font, fontSize=9, leading=12
    )
    normal_right = ParagraphStyle(
        "BodyLVRight", parent=normal, alignment=2
    )
    small = ParagraphStyle(
        "SmallLV", parent=styles["Normal"], fontName=font, fontSize=8, leading=10
    )
    small_bold = ParagraphStyle(
        "SmallLVBold", parent=small, fontName=font_bold
    )
    label = ParagraphStyle(
        "LabelLV",
        parent=small,
        fontName=font_bold,
        textColor=colors.Color(0.36, 0.42, 0.45),
        fontSize=8,
        spaceAfter=2,
    )

    is_invoice = document.doc_type == "invoice"
    title = nfc("RĒĶINS") if is_invoice else nfc("PAVADZĪME")

    seller_bits = [
        f"<b>{nfc(document.seller_name)}</b>",
        f"Reģ. Nr.: {nfc(document.seller_reg_nr)}" if document.seller_reg_nr else "",
        f"PVN Nr.: {vat_label(document.seller_vat_nr)}",
        nfc(document.seller_address),
        f"Banka: {nfc(document.seller_bank)}" if document.seller_bank else "",
        f"IBAN: {nfc(document.seller_iban)}" if document.seller_iban else "",
        nfc(document.seller_phone),
        nfc(document.seller_email),
    ]
    title_bits = [
        f"<font size='16'><b>{title}</b></font>",
        f"Nr. <b>{nfc(document.number)}</b>",
        f"Datums: {document.doc_date}",
    ]
    if is_invoice and document.due_date:
        title_bits.append(f"Apmaksas termiņš: {document.due_date}")

    seller_flow: list[Any] = [
        Paragraph(nfc("Pārdevējs") if is_invoice else nfc("Izsniedzējs"), label),
    ]
    logo_name = nfc(getattr(document, "seller_logo_filename", "") or "").strip()
    if logo_name:
        logo_path = FONTS_DIR.parent / "logos" / logo_name
        if logo_path.is_file():
            logo_img = Image(str(logo_path))
            # ~40px / 14mm tall, capped width so logo stays secondary to rekvizīti
            max_w, max_h = 40 * mm, 14 * mm
            iw, ih = float(logo_img.imageWidth), float(logo_img.imageHeight)
            scale = min(max_w / iw, max_h / ih)
            logo_img.drawWidth = iw * scale
            logo_img.drawHeight = ih * scale
            seller_flow.append(logo_img)
            seller_flow.append(Spacer(1, 3))
    seller_flow.append(Paragraph("<br/>".join(filter(None, seller_bits)), small))

    header = Table(
        [
            [
                seller_flow,
                [Paragraph("<br/>".join(title_bits), normal_right)],
            ]
        ],
        colWidths=[100 * mm, 70 * mm],
    )
    header.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )

    buyer_bits = [
        f"<b>{nfc(document.buyer_name)}</b>",
        f"Reģ. Nr.: {nfc(document.buyer_reg_nr)}" if document.buyer_reg_nr else "",
        f"PVN Nr.: {vat_label(document.buyer_vat_nr)}",
        nfc(document.buyer_address),
        nfc(document.buyer_phone),
        nfc(document.buyer_email),
    ]
    buyer_flow = [
        Paragraph(nfc("Pircējs") if is_invoice else nfc("Saņēmējs"), label),
        Paragraph("<br/>".join(filter(None, buyer_bits)), small),
    ]

    story: list[Any] = [header, Spacer(1, 10), *buyer_flow, Spacer(1, 10)]

    table_header = ["Nr.", nfc("Nosaukums"), nfc("Mērv."), nfc("Daudz."), "Cena", "PVN %", "Summa"]
    data: list[list[Any]] = [table_header]
    for idx, line in enumerate(document.lines, start=1):
        data.append(
            [
                str(idx),
                Paragraph(nfc(line.description), small),
                nfc(line.unit),
                f"{line.quantity:g}",
                f"{line.unit_price:.2f}",
                f"{line.vat_rate:g}",
                f"{line.line_subtotal:.2f}",
            ]
        )
    col_widths = [10 * mm, 70 * mm, 15 * mm, 18 * mm, 18 * mm, 15 * mm, 22 * mm]
    lines_table = Table(data, colWidths=col_widths, repeatRows=1)
    lines_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.12, 0.36, 0.30)),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), font_bold),
                ("FONTNAME", (0, 1), (-1, -1), font),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(lines_table)
    story.append(Spacer(1, 8))

    currency = nfc(document.currency or "EUR")
    totals_data = [
        [nfc("Summa bez PVN"), f"{document.subtotal:.2f} {currency}"],
        ["PVN", f"{document.vat_total:.2f} {currency}"],
        [nfc("Kopā"), f"{document.total:.2f} {currency}"],
    ]
    totals_table = Table(totals_data, colWidths=[45 * mm, 35 * mm], hAlign="RIGHT")
    totals_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 1), font),
                ("FONTNAME", (0, 2), (-1, 2), font_bold),
                ("FONTSIZE", (0, 0), (-1, 1), 9),
                ("FONTSIZE", (0, 2), (-1, 2), 11),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("LINEABOVE", (0, 2), (-1, 2), 0.5, colors.grey),
                ("TOPPADDING", (0, 2), (-1, 2), 6),
            ]
        )
    )
    story.append(totals_table)
    story.append(Spacer(1, 12))
    story.append(
        Paragraph(
            f"<b>{nfc('Summa vārdiem:')}</b> {amount_in_words_eur(document.total)}",
            small,
        )
    )
    story.append(Paragraph(LEGAL_LINE, small))
    if document.notes:
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"Piezīmes: {nfc(document.notes)}", small))
    if not is_invoice:
        story.append(Spacer(1, 20))
        story.append(
            Paragraph(
                nfc("Izsniedza: ________________ &nbsp;&nbsp;&nbsp; Saņēma: ________________"),
                normal,
            )
        )

    doc_pdf.build(story)
    return buffer.getvalue()


def generate_pdf(document: Any) -> tuple[bytes, str]:
    """Return (pdf_bytes, engine_name)."""
    if weasyprint_available():
        try:
            html = render_document_html(document)
            return html_to_pdf_weasy(html), "weasyprint"
        except Exception as exc:
            logger.exception("WeasyPrint failed, falling back to ReportLab: %s", exc)
    return document_to_pdf_reportlab(document), "reportlab"
