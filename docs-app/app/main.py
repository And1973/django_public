from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Optional

from fastapi import Depends, FastAPI, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.auth import (
    check_password,
    create_session_token,
    is_authenticated,
    require_login,
)
from app.config import BASE_DIR, SESSION_COOKIE, SESSION_MAX_AGE, VAT_RATE_DEFAULT
from app.database import Base, SessionLocal, engine, get_db
from app.models import Buyer, Document, DocumentLine, Product, Seller
from app.services.calc import calc_document
from app.services.numbering import next_document_number
from app.services.pdf import generate_pdf, weasyprint_available
from app.services.seed import seed_sellers

app = FastAPI(title="Rēķini un pavadzīmes")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "app" / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

def render(request: Request, name: str, context: dict | None = None, status_code: int = 200):
    ctx = dict(context or {})
    ctx.setdefault("request", request)
    return templates.TemplateResponse(request, name, ctx, status_code=status_code)



@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_sellers(db)
    finally:
        db.close()


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _form_lines(form: Any) -> list[dict]:
    descriptions = form.getlist("line_description")
    units = form.getlist("line_unit")
    quantities = form.getlist("line_quantity")
    prices = form.getlist("line_unit_price")
    vats = form.getlist("line_vat_rate")
    lines = []
    for i, desc in enumerate(descriptions):
        lines.append(
            {
                "description": desc,
                "unit": units[i] if i < len(units) else "gab.",
                "quantity": quantities[i] if i < len(quantities) else 1,
                "unit_price": prices[i] if i < len(prices) else 0,
                "vat_rate": vats[i] if i < len(vats) else VAT_RATE_DEFAULT,
            }
        )
    return lines


def _upsert_buyer(
    db: Session,
    *,
    buyer_id: str | None,
    name: str,
    reg_nr: str,
    vat_nr: str,
    address: str,
    phone: str,
    email: str,
    save_buyer: bool,
) -> Buyer | None:
    name = (name or "").strip()
    if not name:
        return None
    buyer: Buyer | None = None
    if buyer_id:
        try:
            buyer = db.get(Buyer, int(buyer_id))
        except ValueError:
            buyer = None
    if buyer is None and save_buyer:
        buyer = Buyer(name=name)
        db.add(buyer)
    if buyer is not None:
        buyer.name = name
        buyer.reg_nr = (reg_nr or "").strip()
        buyer.vat_nr = (vat_nr or "").strip()
        buyer.address = (address or "").strip()
        buyer.phone = (phone or "").strip()
        buyer.email = (email or "").strip()
        db.flush()
        return buyer
    # ephemeral buyer object (not persisted)
    return Buyer(
        name=name,
        reg_nr=(reg_nr or "").strip(),
        vat_nr=(vat_nr or "").strip(),
        address=(address or "").strip(),
        phone=(phone or "").strip(),
        email=(email or "").strip(),
    )


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    if is_authenticated(request):
        return RedirectResponse("/documents", status_code=303)
    return RedirectResponse("/login", status_code=303)


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if is_authenticated(request):
        return RedirectResponse("/documents", status_code=303)
    return render(request, "login.html", {"error": None},
    )


@app.post("/login", response_class=HTMLResponse)
def login_submit(request: Request, password: str = Form(...)):
    if not check_password(password):
        return render(request, "login.html", {"error": "Nepareiza parole."},
            status_code=401,
        )
    response = RedirectResponse("/documents", status_code=303)
    response.set_cookie(
        SESSION_COOKIE,
        create_session_token(),
        max_age=SESSION_MAX_AGE,
        httponly=True,
        samesite="lax",
    )
    return response


@app.post("/logout")
def logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie(SESSION_COOKIE)
    return response


@app.get("/documents", response_class=HTMLResponse)
def document_list(
    request: Request,
    db: Session = Depends(get_db),
    doc_type: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
):
    redirect = require_login(request)
    if redirect:
        return redirect

    stmt = select(Document).options(joinedload(Document.lines)).order_by(
        Document.doc_date.desc(), Document.id.desc()
    )
    if doc_type in ("invoice", "delivery_note"):
        stmt = stmt.where(Document.doc_type == doc_type)
    d_from = _parse_date(date_from)
    d_to = _parse_date(date_to)
    if d_from:
        stmt = stmt.where(Document.doc_date >= d_from)
    if d_to:
        stmt = stmt.where(Document.doc_date <= d_to)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                Document.number.ilike(like),
                Document.buyer_name.ilike(like),
                Document.seller_name.ilike(like),
            )
        )
    documents = db.scalars(stmt).unique().all()
    return render(request, "documents/list.html", {"documents": documents,
            "filters": {
                "doc_type": doc_type or "",
                "date_from": date_from or "",
                "date_to": date_to or "",
                "q": q or "",
            },
        },
    )


@app.get("/documents/new", response_class=HTMLResponse)
def document_new(
    request: Request,
    db: Session = Depends(get_db),
    doc_type: Optional[str] = Query("invoice"),
    seller_id: Optional[int] = Query(None),
):
    redirect = require_login(request)
    if redirect:
        return redirect
    if doc_type not in ("invoice", "delivery_note"):
        doc_type = "invoice"
    sellers = db.scalars(
        select(Seller).where(Seller.is_active.is_(True)).order_by(Seller.sort_order)
    ).all()
    products = db.scalars(
        select(Product).where(Product.is_active.is_(True)).order_by(Product.name)
    ).all()
    selected = None
    if seller_id:
        selected = db.get(Seller, seller_id)
    return render(request, "documents/form.html", {"doc_type": doc_type,
            "sellers": sellers,
            "selected_seller": selected,
            "products": products,
            "today": date.today().isoformat(),
            "due_default": (date.today() + timedelta(days=14)).isoformat(),
            "vat_default": VAT_RATE_DEFAULT,
            "error": None,
            "form": {},
        },
    )


@app.get("/api/buyers")
def search_buyers(
    request: Request,
    db: Session = Depends(get_db),
    q: str = Query(""),
):
    redirect = require_login(request)
    if redirect:
        return redirect
    stmt = select(Buyer).order_by(Buyer.name).limit(20)
    if q.strip():
        like = f"%{q.strip()}%"
        stmt = select(Buyer).where(
            or_(Buyer.name.ilike(like), Buyer.reg_nr.ilike(like), Buyer.vat_nr.ilike(like))
        ).order_by(Buyer.name).limit(20)
    buyers = db.scalars(stmt).all()
    return [
        {
            "id": b.id,
            "name": b.name,
            "reg_nr": b.reg_nr,
            "vat_nr": b.vat_nr,
            "address": b.address,
            "phone": b.phone,
            "email": b.email,
        }
        for b in buyers
    ]


@app.get("/api/products")
def search_products(
    request: Request,
    db: Session = Depends(get_db),
    q: str = Query(""),
):
    redirect = require_login(request)
    if redirect:
        return redirect
    stmt = select(Product).where(Product.is_active.is_(True)).order_by(Product.name).limit(30)
    if q.strip():
        like = f"%{q.strip()}%"
        stmt = (
            select(Product)
            .where(Product.is_active.is_(True), or_(Product.name.ilike(like), Product.sku.ilike(like)))
            .order_by(Product.name)
            .limit(30)
        )
    products = db.scalars(stmt).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "unit": p.unit,
            "price": p.price,
            "vat_rate": p.vat_rate,
        }
        for p in products
    ]


@app.post("/documents/new", response_class=HTMLResponse)
async def document_create(request: Request, db: Session = Depends(get_db)):
    redirect = require_login(request)
    if redirect:
        return redirect

    form = await request.form()
    doc_type = form.get("doc_type") or "invoice"
    if doc_type not in ("invoice", "delivery_note"):
        doc_type = "invoice"

    sellers = db.scalars(
        select(Seller).where(Seller.is_active.is_(True)).order_by(Seller.sort_order)
    ).all()
    products = db.scalars(
        select(Product).where(Product.is_active.is_(True)).order_by(Product.name)
    ).all()

    def render_error(msg: str, selected: Seller | None = None):
        return render(request, "documents/form.html", {"doc_type": doc_type,
                "sellers": sellers,
                "selected_seller": selected,
                "products": products,
                "today": form.get("doc_date") or date.today().isoformat(),
                "due_default": form.get("due_date") or "",
                "vat_default": VAT_RATE_DEFAULT,
                "error": msg,
                "form": dict(form),
            },
            status_code=400,
        )

    try:
        seller_id = int(form.get("seller_id") or 0)
    except ValueError:
        seller_id = 0
    seller = db.get(Seller, seller_id) if seller_id else None
    if not seller:
        return render_error("Izvēlieties pārdevēju.")

    doc_date = _parse_date(form.get("doc_date")) or date.today()
    due_date = _parse_date(form.get("due_date")) if doc_type == "invoice" else None
    buyer_name = (form.get("buyer_name") or "").strip()
    if not buyer_name:
        return render_error("Norādiet pircēja nosaukumu.", seller)

    raw_lines = _form_lines(form)
    totals = calc_document(raw_lines)
    if not totals.lines:
        return render_error("Pievienojiet vismaz vienu rindu ar nosaukumu.", seller)

    save_buyer = form.get("save_buyer") == "on"
    buyer = _upsert_buyer(
        db,
        buyer_id=form.get("buyer_id"),
        name=buyer_name,
        reg_nr=form.get("buyer_reg_nr") or "",
        vat_nr=form.get("buyer_vat_nr") or "",
        address=form.get("buyer_address") or "",
        phone=form.get("buyer_phone") or "",
        email=form.get("buyer_email") or "",
        save_buyer=save_buyer or bool(form.get("buyer_id")),
    )

    number = next_document_number(db, doc_type, doc_date)
    document = Document(
        doc_type=doc_type,
        number=number,
        doc_date=doc_date,
        due_date=due_date,
        seller_id=seller.id,
        buyer_id=buyer.id if buyer and getattr(buyer, "id", None) else None,
        seller_name=seller.name,
        seller_reg_nr=seller.reg_nr,
        seller_vat_nr=seller.vat_nr,
        seller_address=seller.address,
        seller_bank=seller.bank,
        seller_iban=seller.iban,
        seller_phone=seller.phone,
        seller_email=seller.email,
        buyer_name=buyer_name,
        buyer_reg_nr=(form.get("buyer_reg_nr") or "").strip(),
        buyer_vat_nr=(form.get("buyer_vat_nr") or "").strip(),
        buyer_address=(form.get("buyer_address") or "").strip(),
        buyer_phone=(form.get("buyer_phone") or "").strip(),
        buyer_email=(form.get("buyer_email") or "").strip(),
        buyer_vat_checked=form.get("buyer_vat_checked") == "on",
        currency="EUR",
        notes=(form.get("notes") or "").strip(),
        subtotal=totals.subtotal,
        vat_total=totals.vat_total,
        total=totals.total,
    )
    for i, line in enumerate(totals.lines):
        document.lines.append(
            DocumentLine(
                position=i + 1,
                description=line.description,
                unit=line.unit,
                quantity=line.quantity,
                unit_price=line.unit_price,
                vat_rate=line.vat_rate,
                line_subtotal=line.line_subtotal,
                line_vat=line.line_vat,
                line_total=line.line_total,
            )
        )
    db.add(document)
    db.commit()
    db.refresh(document)
    return RedirectResponse(f"/documents/{document.id}", status_code=303)


@app.get("/documents/{doc_id}", response_class=HTMLResponse)
def document_detail(
    request: Request,
    doc_id: int,
    db: Session = Depends(get_db),
):
    redirect = require_login(request)
    if redirect:
        return redirect
    document = db.scalar(
        select(Document)
        .options(joinedload(Document.lines))
        .where(Document.id == doc_id)
    )
    if not document:
        return RedirectResponse("/documents", status_code=303)
    return render(request, "documents/detail.html", {"doc": document,
            "pdf_engine": "weasyprint" if weasyprint_available() else "reportlab",
        },
    )


@app.get("/documents/{doc_id}/pdf")
def document_pdf(
    request: Request,
    doc_id: int,
    db: Session = Depends(get_db),
    download: int = Query(0),
):
    redirect = require_login(request)
    if redirect:
        return redirect
    document = db.scalar(
        select(Document)
        .options(joinedload(Document.lines))
        .where(Document.id == doc_id)
    )
    if not document:
        return RedirectResponse("/documents", status_code=303)
    pdf_bytes, _engine = generate_pdf(document)
    headers = {}
    filename = f"{document.number}.pdf"
    disposition = "attachment" if download else "inline"
    headers["Content-Disposition"] = f'{disposition}; filename="{filename}"'
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)


@app.get("/products", response_class=HTMLResponse)
def products_page(request: Request, db: Session = Depends(get_db)):
    redirect = require_login(request)
    if redirect:
        return redirect
    products = db.scalars(select(Product).order_by(Product.name)).all()
    return render(request, "products.html", {"products": products, "error": None},
    )


@app.post("/products", response_class=HTMLResponse)
def products_create(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    unit: str = Form("gab."),
    price: float = Form(0),
    vat_rate: float = Form(VAT_RATE_DEFAULT),
    sku: str = Form(""),
):
    redirect = require_login(request)
    if redirect:
        return redirect
    name = name.strip()
    if name:
        db.add(
            Product(
                name=name,
                unit=unit.strip() or "gab.",
                price=price,
                vat_rate=vat_rate,
                sku=sku.strip(),
            )
        )
        db.commit()
    return RedirectResponse("/products", status_code=303)


@app.get("/health")
def health():
    return {
        "ok": True,
        "pdf": "weasyprint" if weasyprint_available() else "reportlab",
        "time": datetime.utcnow().isoformat() + "Z",
    }
