import json
import sys
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()


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
