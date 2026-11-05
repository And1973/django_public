from __future__ import annotations

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.config import PASSWORD, SECRET_KEY, SESSION_COOKIE, SESSION_MAX_AGE

_serializer = URLSafeTimedSerializer(SECRET_KEY, salt="docs-app-auth")


def create_session_token() -> str:
    return _serializer.dumps({"auth": True})


def verify_session_token(token: str) -> bool:
    try:
        data = _serializer.loads(token, max_age=SESSION_MAX_AGE)
        return bool(data.get("auth"))
    except (BadSignature, SignatureExpired):
        return False


def check_password(password: str) -> bool:
    return password == PASSWORD


def is_authenticated(request: Request) -> bool:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return False
    return verify_session_token(token)


def require_login(request: Request) -> RedirectResponse | None:
    if is_authenticated(request):
        return None
    return RedirectResponse(url="/login", status_code=303)
