from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Seller
from app.textutil import nfc

# Real company rekvizīti (synced on every startup by sort_order).
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
        "sort_order": 3,
    },
]


def seed_sellers(db: Session) -> None:
    """Insert or update the three canonical sellers; deactivate any extras."""
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
