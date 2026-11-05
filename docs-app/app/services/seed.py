from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Seller

# Placeholder rekvizīti — replace with real company details before production use.
PLACEHOLDER_SELLERS = [
    {
        "name": "SIA Ziemeļu Tirdzniecība",
        "reg_nr": "40003000001",
        "vat_nr": "LV40003000001",
        "address": "Brīvības iela 1, Rīga, LV-1010",
        "bank": "Swedbank AS",
        "iban": "LV00HABA0000000000001",
        "phone": "+371 20000001",
        "email": "info@ziemelu-demo.lv",
        "sort_order": 1,
    },
    {
        "name": "SIA Rīgas Piegādes",
        "reg_nr": "40003000002",
        "vat_nr": "LV40003000002",
        "address": "Maskavas iela 240, Rīga, LV-1063",
        "bank": "SEB banka AS",
        "iban": "LV00UNLA0000000000002",
        "phone": "+371 20000002",
        "email": "office@rigas-piegades-demo.lv",
        "sort_order": 2,
    },
    {
        "name": "IK Latgales Preces",
        "reg_nr": "40003000003",
        "vat_nr": "LV40003000003",
        "address": "Rīgas iela 15, Daugavpils, LV-5401",
        "bank": "Luminor Bank AS",
        "iban": "LV00RIKO0000000000003",
        "phone": "+371 20000003",
        "email": "veikals@latgale-demo.lv",
        "sort_order": 3,
    },
]


def seed_sellers(db: Session) -> None:
    existing = db.scalar(select(Seller).limit(1))
    if existing:
        return
    for row in PLACEHOLDER_SELLERS:
        db.add(Seller(**row, is_active=True))
    db.commit()
