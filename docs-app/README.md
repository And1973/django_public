# Rēķini un pavadzīmes

Atsevišķa tīmekļa lietotne latviešu rēķiniem un pavadzīmēm (FastAPI + Jinja2 + SQLite).

**Neaizskar** `order/` — šis ir neatkarīgs projekts mapē `docs-app/`.

## Prasības

- Python 3.11+
- Pip

PDF: mēģina **WeasyPrint**; ja sistēmas bibliotēkas nav pieejamas, automātiski izmanto **ReportLab**.

## Palaišana lokāli

```bash
cd docs-app
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # iestatiet DOCS_APP_PASSWORD
uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
```

Atveriet http://127.0.0.1:8080 un ievadiet paroli no `.env` (`DOCS_APP_PASSWORD`).

Noklusējuma parole demom (ja `.env` nav): `docs-demo`.

## Plūsma

1. Pieteikšanās (viena parole)
2. Dokumentu saraksts (filtrs: tips / datums / meklēšana)
3. Jauns dokuments: tips → 3 pārdevēju pogas → pircējs → rindas → automātiskās summas → saglabāt → PDF priekšskatījums / lejupielāde

## Pārdevēji (seed)

Pie starta sinhronizējas 3 pārdevēji (`app/services/seed.py`):

1. **Madeks SIA** — PVN LV40203446165, Matīsa iela 91-17, Swedbank  
2. **Zauers Classic Cars SIA** — PVN LV40203644857, Viestura prospekts 49-18  
3. **Zauers Tenisa Klubs** — reģ. 40008266820, **nav PVN**

UI un PDF izmanto komplektēto **DejaVu Sans** (`app/static/fonts/`); teksts normalizēts uz NFC.

## Tehniskās piezīmes

- Auth: sesijas sīkdatne (`itsdangerous`), parole no `DOCS_APP_PASSWORD`
- DB: SQLite (`data/docs.db`)
- PVN pārbaude: tikai manuāla atzīme (bez VIES)
- Dokumentu numuri: `REK-YYYY-####` / `PAV-YYYY-####`
- Veselības pārbaude: `GET /health`
