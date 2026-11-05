from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from app.textutil import nfc

_ONES = [
    "",
    "viens",
    "divi",
    "trīs",
    "četri",
    "pieci",
    "seši",
    "septiņi",
    "astoņi",
    "deviņi",
]
_TEENS = [
    "desmit",
    "vienpadsmit",
    "divpadsmit",
    "trīspadsmit",
    "četrpadsmit",
    "piecpadsmit",
    "sešpadsmit",
    "septiņpadsmit",
    "astoņpadsmit",
    "deviņpadsmit",
]
_TENS = [
    "",
    "",
    "divdesmit",
    "trīsdesmit",
    "četrdesmit",
    "piecdesmit",
    "sešdesmit",
    "septiņdesmit",
    "astoņdesmit",
    "deviņdesmit",
]


def _under_thousand(n: int) -> str:
    if n <= 0:
        return ""
    parts: list[str] = []
    hundreds = n // 100
    rest = n % 100
    if hundreds:
        if hundreds == 1:
            parts.append("simts")
        else:
            parts.append(f"{_ONES[hundreds]} simti")
    if rest:
        if rest < 10:
            parts.append(_ONES[rest])
        elif rest < 20:
            parts.append(_TEENS[rest - 10])
        else:
            tens = rest // 10
            ones = rest % 10
            if ones:
                parts.append(f"{_TENS[tens]} {_ONES[ones]}")
            else:
                parts.append(_TENS[tens])
    return " ".join(parts)


def integer_to_latvian(n: int) -> str:
    if n < 0:
        return nfc(f"mīnus {integer_to_latvian(-n)}")
    if n == 0:
        return "nulle"
    parts: list[str] = []
    millions = n // 1_000_000
    thousands = (n % 1_000_000) // 1000
    rest = n % 1000
    if millions:
        if millions == 1:
            parts.append("viens miljons")
        else:
            words = _under_thousand(millions)
            # 2–9: miljoni; teens etc. also miljoni
            parts.append(f"{words} miljoni")
    if thousands:
        if thousands == 1:
            parts.append("viens tūkstotis")
        else:
            parts.append(f"{_under_thousand(thousands)} tūkstoši")
    if rest:
        parts.append(_under_thousand(rest))
    return " ".join(parts)


def _euro_word(euros: int) -> str:
    return "eiro"


def _cent_word(cents: int) -> str:
    if cents == 1:
        return "cents"
    return "centi"


def amount_in_words_eur(amount: float | Decimal | str) -> str:
    """Latvian amount-in-words for EUR + cents, NFC-normalized."""
    value = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if value < 0:
        value = -value
    euros = int(value)
    cents = int((value - euros) * 100)
    euro_words = integer_to_latvian(euros)
    cent_words = integer_to_latvian(cents)
    text = (
        f"{euro_words} {_euro_word(euros)} un {cent_words} {_cent_word(cents)}"
    )
    # Capitalize first letter for document footer style
    text = text[:1].upper() + text[1:] if text else text
    return nfc(text)
