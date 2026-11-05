from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DocumentSequence

PREFIXES = {
    "invoice": "REK",
    "delivery_note": "PAV",
}


def next_document_number(db: Session, doc_type: str, doc_date: date | None = None) -> str:
    if doc_type not in PREFIXES:
        raise ValueError(f"Unknown doc_type: {doc_type}")
    year = (doc_date or date.today()).year
    seq = db.scalar(
        select(DocumentSequence).where(
            DocumentSequence.doc_type == doc_type,
            DocumentSequence.year == year,
        )
    )
    if seq is None:
        seq = DocumentSequence(doc_type=doc_type, year=year, last_number=0)
        db.add(seq)
        db.flush()
    seq.last_number += 1
    db.flush()
    return f"{PREFIXES[doc_type]}-{year}-{seq.last_number:04d}"
