from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LineCalc:
    description: str
    unit: str
    quantity: float
    unit_price: float
    vat_rate: float
    line_subtotal: float
    line_vat: float
    line_total: float


@dataclass
class DocTotals:
    lines: list[LineCalc]
    subtotal: float
    vat_total: float
    total: float


def round_money(value: float) -> float:
    return round(value + 1e-9, 2)


def calc_line(
    description: str,
    unit: str,
    quantity: float,
    unit_price: float,
    vat_rate: float,
) -> LineCalc:
    subtotal = round_money(quantity * unit_price)
    vat = round_money(subtotal * vat_rate / 100.0)
    total = round_money(subtotal + vat)
    return LineCalc(
        description=description,
        unit=unit or "gab.",
        quantity=quantity,
        unit_price=unit_price,
        vat_rate=vat_rate,
        line_subtotal=subtotal,
        line_vat=vat,
        line_total=total,
    )


def calc_document(raw_lines: list[dict]) -> DocTotals:
    lines: list[LineCalc] = []
    for raw in raw_lines:
        desc = (raw.get("description") or "").strip()
        if not desc:
            continue
        try:
            qty = float(raw.get("quantity") or 0)
            price = float(raw.get("unit_price") or 0)
            vat = float(raw.get("vat_rate") if raw.get("vat_rate") not in (None, "") else 21)
        except (TypeError, ValueError):
            continue
        lines.append(
            calc_line(
                description=desc,
                unit=(raw.get("unit") or "gab.").strip() or "gab.",
                quantity=qty,
                unit_price=price,
                vat_rate=vat,
            )
        )
    subtotal = round_money(sum(l.line_subtotal for l in lines))
    vat_total = round_money(sum(l.line_vat for l in lines))
    total = round_money(subtotal + vat_total)
    return DocTotals(lines=lines, subtotal=subtotal, vat_total=vat_total, total=total)
