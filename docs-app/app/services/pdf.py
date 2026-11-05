from __future__ import annotations

import io
import logging
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.config import BASE_DIR

logger = logging.getLogger(__name__)

TEMPLATES_DIR = BASE_DIR / "app" / "templates"
_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)

_WEASY_OK: bool | None = None


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


def render_document_html(document: Any) -> str:
    template_name = (
        "pdf/invoice.html"
        if document.doc_type == "invoice"
        else "pdf/delivery_note.html"
    )
    template = _env.get_template(template_name)
    return template.render(doc=document, engine="weasyprint")


def html_to_pdf_weasy(html: str) -> bytes:
    from weasyprint import HTML

    return HTML(string=html, base_url=str(TEMPLATES_DIR)).write_pdf()


def document_to_pdf_reportlab(document: Any) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

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
        fontSize=16,
        spaceAfter=8,
    )
    normal = ParagraphStyle("BodyLV", parent=styles["Normal"], fontSize=9, leading=12)
    small = ParagraphStyle("SmallLV", parent=styles["Normal"], fontSize=8, leading=10)

    is_invoice = document.doc_type == "invoice"
    title = "RĒĶINS" if is_invoice else "PAVADZĪME"

    story: list[Any] = [
        Paragraph(title, title_style),
        Paragraph(f"Nr. <b>{document.number}</b> &nbsp;&nbsp; Datums: {document.doc_date}", normal),
    ]
    if is_invoice and document.due_date:
        story.append(Paragraph(f"Apmaksas termiņš: {document.due_date}", normal))
    story.append(Spacer(1, 8))

    parties = [
        [
            Paragraph("<b>Pārdevējs / Izsniedzējs</b>", small),
            Paragraph("<b>Pircējs / Saņēmējs</b>", small),
        ],
        [
            Paragraph(
                "<br/>".join(
                    filter(
                        None,
                        [
                            document.seller_name,
                            f"Reģ. Nr.: {document.seller_reg_nr}" if document.seller_reg_nr else "",
                            f"PVN Nr.: {document.seller_vat_nr}" if document.seller_vat_nr else "",
                            document.seller_address,
                            f"Banka: {document.seller_bank}" if document.seller_bank else "",
                            f"IBAN: {document.seller_iban}" if document.seller_iban else "",
                            document.seller_phone,
                            document.seller_email,
                        ],
                    )
                ),
                small,
            ),
            Paragraph(
                "<br/>".join(
                    filter(
                        None,
                        [
                            document.buyer_name,
                            f"Reģ. Nr.: {document.buyer_reg_nr}" if document.buyer_reg_nr else "",
                            f"PVN Nr.: {document.buyer_vat_nr}" if document.buyer_vat_nr else "",
                            document.buyer_address,
                            document.buyer_phone,
                            document.buyer_email,
                        ],
                    )
                ),
                small,
            ),
        ],
    ]
    party_table = Table(parties, colWidths=[85 * mm, 85 * mm])
    party_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOX", (0, 0), (-1, -1), 0.4, colors.grey),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.93, 0.93, 0.93)),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(party_table)
    story.append(Spacer(1, 10))

    header = ["Nr.", "Nosaukums", "Mērv.", "Daudz.", "Cena", "PVN %", "Summa"]
    data: list[list[Any]] = [header]
    for idx, line in enumerate(document.lines, start=1):
        data.append(
            [
                str(idx),
                Paragraph(line.description, small),
                line.unit,
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
                ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.2, 0.25, 0.3)),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
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
    story.append(Paragraph(f"Bez PVN: <b>{document.subtotal:.2f} {document.currency}</b>", normal))
    story.append(Paragraph(f"PVN: <b>{document.vat_total:.2f} {document.currency}</b>", normal))
    story.append(Paragraph(f"Kopā: <b>{document.total:.2f} {document.currency}</b>", title_style))
    if document.notes:
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"Piezīmes: {document.notes}", small))
    if not is_invoice:
        story.append(Spacer(1, 20))
        story.append(
            Paragraph(
                "Izsniedza: ________________ &nbsp;&nbsp;&nbsp; Saņēma: ________________",
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
