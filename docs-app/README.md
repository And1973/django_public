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

## Placeholder pārdevēji

Pirmajā startā tiek ielādēti 3 demo pārdevēji (izdomāti rekvizīti):

1. SIA Ziemeļu Tirdzniecība  
2. SIA Rīgas Piegādes  
3. IK Latgales Preces  

Pirms ražošanas lietojuma aizstājiet tos ar reāliem rekvizītiem (DB vai `app/services/seed.py`).

## Tehniskās piezīmes

- Auth: sesijas sīkdatne (`itsdangerous`), parole no `DOCS_APP_PASSWORD`
- DB: SQLite (`data/docs.db`)
- PVN pārbaude: tikai manuāla atzīme (bez VIES)
- Dokumentu numuri: `REK-YYYY-####` / `PAV-YYYY-####`
- Veselības pārbaude: `GET /health`
