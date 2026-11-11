from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

PASSWORD = os.getenv("DOCS_APP_PASSWORD", "docs-demo")
SECRET_KEY = os.getenv("DOCS_APP_SECRET", "dev-secret-change-me")
DATABASE_URL = os.getenv(
    "DOCS_APP_DB",
    f"sqlite:///{(DATA_DIR / 'docs.db').as_posix()}",
)
SESSION_COOKIE = "docs_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 7  # 7 days
VAT_RATE_DEFAULT = 21.0
