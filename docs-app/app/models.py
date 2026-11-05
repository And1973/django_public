from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Seller(Base):
    __tablename__ = "sellers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    reg_nr: Mapped[str] = mapped_column(String(64), default="")
    vat_nr: Mapped[str] = mapped_column(String(64), default="")
    address: Mapped[str] = mapped_column(Text, default="")
    bank: Mapped[str] = mapped_column(String(255), default="")
    iban: Mapped[str] = mapped_column(String(64), default="")
    phone: Mapped[str] = mapped_column(String(64), default="")
    email: Mapped[str] = mapped_column(String(255), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    documents: Mapped[list["Document"]] = relationship(back_populates="seller")


class Buyer(Base):
    __tablename__ = "buyers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    reg_nr: Mapped[str] = mapped_column(String(64), default="")
    vat_nr: Mapped[str] = mapped_column(String(64), default="")
    address: Mapped[str] = mapped_column(Text, default="")
    phone: Mapped[str] = mapped_column(String(64), default="")
    email: Mapped[str] = mapped_column(String(255), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    documents: Mapped[list["Document"]] = relationship(back_populates="buyer")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    unit: Mapped[str] = mapped_column(String(32), default="gab.")
    price: Mapped[float] = mapped_column(Float, default=0.0)
    vat_rate: Mapped[float] = mapped_column(Float, default=21.0)
    sku: Mapped[str] = mapped_column(String(64), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class DocumentSequence(Base):
    __tablename__ = "document_sequences"
    __table_args__ = (UniqueConstraint("doc_type", "year", name="uq_seq_type_year"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    doc_type: Mapped[str] = mapped_column(String(32), nullable=False)  # invoice | delivery_note
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    last_number: Mapped[int] = mapped_column(Integer, default=0)


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    doc_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    number: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    doc_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    seller_id: Mapped[int] = mapped_column(ForeignKey("sellers.id"), nullable=False)
    buyer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("buyers.id"), nullable=True)

    # Snapshot fields (frozen at save time)
    seller_name: Mapped[str] = mapped_column(String(255), default="")
    seller_reg_nr: Mapped[str] = mapped_column(String(64), default="")
    seller_vat_nr: Mapped[str] = mapped_column(String(64), default="")
    seller_address: Mapped[str] = mapped_column(Text, default="")
    seller_bank: Mapped[str] = mapped_column(String(255), default="")
    seller_iban: Mapped[str] = mapped_column(String(64), default="")
    seller_phone: Mapped[str] = mapped_column(String(64), default="")
    seller_email: Mapped[str] = mapped_column(String(255), default="")

    buyer_name: Mapped[str] = mapped_column(String(255), default="")
    buyer_reg_nr: Mapped[str] = mapped_column(String(64), default="")
    buyer_vat_nr: Mapped[str] = mapped_column(String(64), default="")
    buyer_address: Mapped[str] = mapped_column(Text, default="")
    buyer_phone: Mapped[str] = mapped_column(String(64), default="")
    buyer_email: Mapped[str] = mapped_column(String(255), default="")
    buyer_vat_checked: Mapped[bool] = mapped_column(Boolean, default=False)

    currency: Mapped[str] = mapped_column(String(8), default="EUR")
    notes: Mapped[str] = mapped_column(Text, default="")

    subtotal: Mapped[float] = mapped_column(Float, default=0.0)
    vat_total: Mapped[float] = mapped_column(Float, default=0.0)
    total: Mapped[float] = mapped_column(Float, default=0.0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    seller: Mapped[Seller] = relationship(back_populates="documents")
    buyer: Mapped[Optional[Buyer]] = relationship(back_populates="documents")
    lines: Mapped[list["DocumentLine"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="DocumentLine.position",
    )


class DocumentLine(Base):
    __tablename__ = "document_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    unit: Mapped[str] = mapped_column(String(32), default="gab.")
    quantity: Mapped[float] = mapped_column(Float, default=1.0)
    unit_price: Mapped[float] = mapped_column(Float, default=0.0)
    vat_rate: Mapped[float] = mapped_column(Float, default=21.0)
    line_subtotal: Mapped[float] = mapped_column(Float, default=0.0)
    line_vat: Mapped[float] = mapped_column(Float, default=0.0)
    line_total: Mapped[float] = mapped_column(Float, default=0.0)

    document: Mapped[Document] = relationship(back_populates="lines")
