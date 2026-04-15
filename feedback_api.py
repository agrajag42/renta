import json
import os
import hmac
import hashlib
import base64
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

SESSION_SECRET = os.environ.get("SESSION_SECRET", "dev-secret-change-me")
REQUIRED_TIER = "friends"
TIER_RANK = {"public": 0, "friends": 1, "family": 2, "admin": 3}
ACCOUNTS = {
    "friends": "friends",
    "family": "family",
    "admin": "admin",
}
LOGIN_URL = "/"


def _verify_session(token):
    """Verify HMAC-signed session cookie (same scheme as homepage app)."""
    if not token or "." not in token:
        return None
    value, sig_b64 = token.rsplit(".", 1)
    expected = hmac.new(SESSION_SECRET.encode(), value.encode(), hashlib.sha256).digest()
    pad = 4 - len(sig_b64) % 4
    try:
        actual = base64.urlsafe_b64decode(sig_b64 + "=" * pad)
    except Exception:
        return None
    if hmac.compare_digest(expected, actual):
        return value
    return None


def _check_auth(request: Request):
    """Return username if authenticated at friends tier or above, else None."""
    token = request.cookies.get("__session")
    username = _verify_session(token)
    if not username:
        return None
    tier = ACCOUNTS.get(username)
    if not tier:
        return None
    if TIER_RANK.get(tier, 0) >= TIER_RANK.get(REQUIRED_TIER, 1):
        return username
    return None


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path

    # Health check -- no auth needed
    if path == "/api/health":
        return await call_next(request)

    # Strip /friends/renta prefix if present (Firebase sends full path)
    if path.startswith("/friends/renta"):
        stripped = path[len("/friends/renta"):] or "/"
        request.scope["path"] = stripped

    # Check auth for everything else
    path = request.scope["path"]
    if path.startswith("/api/"):
        # API endpoints: check auth
        user = _check_auth(request)
        if not user:
            return JSONResponse({"error": "unauthorized"}, status_code=401)
        return await call_next(request)

    user = _check_auth(request)
    if not user:
        return_path = str(request.url)
        return RedirectResponse(url=f"{LOGIN_URL}", status_code=302)

    return await call_next(request)


@app.post("/api/feedback")
async def post_feedback(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)

    entry = {
        "name": body.get("name", ""),
        "text": body.get("text", ""),
        "timestamp": body.get("timestamp", datetime.now(timezone.utc).isoformat()),
        "received_at": datetime.now(timezone.utc).isoformat(),
    }

    # Log to stdout as JSON line -- captured by Cloud Logging
    print(json.dumps({"type": "feedback", **entry}), flush=True)

    # Also append to local file (ephemeral, but useful for debugging)
    try:
        with open("/tmp/feedback.json", "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass

    return JSONResponse({"status": "ok"})


@app.get("/api/feedback")
async def get_feedback(request: Request):
    token = request.query_params.get("token", "")
    if token != "renta-feedback-2026":
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    entries = []
    try:
        with open("/tmp/feedback.json", "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
    except FileNotFoundError:
        pass

    return JSONResponse({"feedback": entries, "count": len(entries)})


@app.get("/api/health")
async def health():
    return JSONResponse({"status": "ok"})


# Serve static files (index.html) for everything else
app.mount("/", StaticFiles(directory="/usr/share/nginx/html/friends/renta", html=True), name="static")
