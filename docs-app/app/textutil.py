from __future__ import annotations

import unicodedata
from typing import Any


def nfc(value: Any) -> str:
    """Normalize text to NFC so Latvian diacritics are precomposed."""
    if value is None:
        return ""
    return unicodedata.normalize("NFC", str(value))


def vat_label(vat_nr: str | None) -> str:
    vat = nfc(vat_nr).strip()
    return vat if vat else "nav PVN"
