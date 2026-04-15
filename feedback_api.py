import json
import os
import hmac
import hashlib
import base64
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse

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
INDEX_PATH = "/usr/share/nginx/html/friends/renta/index.html"

# Load index.html at startup
_index_html = ""
try:
    with open(INDEX_PATH, "r") as f:
        _index_html = f.read()
except FileNotFoundError:
    _index_html = "<h1>index.html not found</h1>"


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


@app.get("/api/health")
async def health():
    return JSONResponse({"status": "ok"})


@app.post("/api/feedback")
@app.post("/friends/renta/api/feedback")
async def post_feedback(request: Request):
    if not _check_auth(request):
        return JSONResponse({"error": "unauthorized"}, status_code=401)

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

    print(json.dumps({"type": "feedback", **entry}), flush=True)

    try:
        with open("/tmp/feedback.json", "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass

    return JSONResponse({"status": "ok"})


@app.get("/api/feedback")
@app.get("/friends/renta/api/feedback")
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


@app.api_route("/friends/renta", methods=["GET"])
@app.api_route("/friends/renta/", methods=["GET"])
@app.api_route("/", methods=["GET"])
async def serve_app(request: Request):
    print(f"SERVE_APP hit: path={request.url.path}", flush=True)
    if not _check_auth(request):
        return RedirectResponse(url=LOGIN_URL, status_code=302)
    return HTMLResponse(_index_html)
