from __future__ import annotations

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.database import engine
from app.models import Seller
from app.textutil import nfc

# Real company rekvizīti (synced on every startup by sort_order).
# Logos only for Classic Cars + Tenisa Klubs (filenames under static/logos/).
SELLERS = [
    {
        "name": nfc("Madeks SIA"),
        "reg_nr": "40203446165",
        "vat_nr": "LV40203446165",
        "address": nfc("Rīga, Matīsa iela 91 - 17, LV-1009"),
        "bank": "Swedbank",
        "iban": "LV04HABA0551053848137",
        "phone": "",
        "email": "",
        "logo_filename": "",
        "sort_order": 1,
    },
    {
        "name": nfc("Zauers Classic Cars SIA"),
        "reg_nr": "40203644857",
        "vat_nr": "LV40203644857",
        "address": nfc("Viestura prospekts 49 – 18, Rīga, LV-1005"),
        "bank": "Swedbank",
        "iban": "LV45HABA0551060964677",
        "phone": "",
        "email": "",
        "logo_filename": "zauers-classic-cars.png",
        "sort_order": 2,
    },
    {
        "name": nfc("Zauers Tenisa Klubs"),
        "reg_nr": "40008266820",
        "vat_nr": "",  # nav PVN
        "address": nfc("Rīga, Viestura prospekts 49 - 18, LV-1005"),
        "bank": "Swedbank",
        "iban": "LV44HABA0551044044209",
        "phone": "",
        "email": "",
        "logo_filename": "zauers-tenisa-klubs.png",
        "sort_order": 3,
    },
]


def ensure_logo_columns() -> None:
    """SQLite create_all does not add columns — patch existing DBs."""
    with engine.begin() as conn:
        for table, column in (
            ("sellers", "logo_filename"),
            ("documents", "seller_logo_filename"),
        ):
            rows = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
            names = {r[1] for r in rows}
            if column not in names:
                conn.execute(
                    text(f"ALTER TABLE {table} ADD COLUMN {column} VARCHAR(255) DEFAULT ''")
                )


def seed_sellers(db: Session) -> None:
    """Insert or update the three canonical sellers; deactivate any extras."""
    ensure_logo_columns()
    keep_ids: list[int] = []
    for row in SELLERS:
        seller = db.scalar(select(Seller).where(Seller.sort_order == row["sort_order"]))
        if seller is None:
            seller = Seller(is_active=True)
            db.add(seller)
        for key, value in row.items():
            setattr(seller, key, value)
        seller.is_active = True
        db.flush()
        keep_ids.append(seller.id)

    extras = db.scalars(select(Seller).where(Seller.id.not_in(keep_ids))).all()
    for extra in extras:
        extra.is_active = False
    db.commit()
