from __future__ import annotations

import unicodedata
from datetime import date, datetime
from typing import Any


def nfc(value: Any) -> str:
    """Normalize text to NFC so Latvian diacritics are precomposed."""
    if value is None:
        return ""
    return unicodedata.normalize("NFC", str(value))


def vat_label(vat_nr: str | None) -> str:
    vat = nfc(vat_nr).strip()
    return vat if vat else "nav PVN"


def is_vat_payer(vat_nr: str | None) -> bool:
    """True when a real VAT number is present (empty = not a VAT payer)."""
    return bool(nfc(vat_nr).strip())


def format_vat_rate(value: Any) -> str:
    """Show VAT % without trailing .0 (21 not 21.0); keep real decimals."""
    if value is None or value == "":
        return ""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value).strip()
    text = f"{number:.10g}"
    if "e" in text.lower():
        text = f"{number:.6f}".rstrip("0").rstrip(".")
    return text or "0"


def format_money_input(value: Any) -> str:
    """Price/Cena inputs always show 2 fractional digits."""
    if value is None or value == "":
        return "0.00"
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return str(value).strip()


def format_date(value: Any) -> str:
    """Display dates as dd-mm-yyyy."""
    if value is None or value == "":
        return ""
    if isinstance(value, datetime):
        value = value.date()
    if isinstance(value, date):
        return value.strftime("%d-%m-%Y")
    text = str(value).strip()
    parsed = parse_date(text)
    return parsed.strftime("%d-%m-%Y") if parsed else text


def parse_date(value: str | None) -> date | None:
    """Accept dd-mm-yyyy, yyyy-mm-dd, and common separators."""
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None
