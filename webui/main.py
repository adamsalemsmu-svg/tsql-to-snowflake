# webui/main.py
from __future__ import annotations

import re
from typing import List, Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Use your existing converter if you like. If not, this route still works because we split batches
# and you can implement tsql_to_snowflake inside neybot.converter.
from neybot.converter import tsql_to_snowflake

app = FastAPI(title="Key Bot - TSQL ➜ Snowflake")

# ---------- Static & Templates ----------
app.mount("/static", StaticFiles(directory="webui/static"), name="static")
templates = Jinja2Templates(directory="webui/templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/healthz")
def healthz():
    return {"ok": True}


# ---------- Conversion Helpers ----------
GO_SPLIT = re.compile(r"^\s*GO\s*;?\s*$", flags=re.IGNORECASE | re.MULTILINE)

def _split_batches(tsql: str) -> List[str]:
    parts = re.split(GO_SPLIT, tsql or "")
    return [p.strip() for p in parts if p and p.strip()]

def _pick_text(body: Optional[dict], raw: str) -> str:
    """
    Accept multiple shapes:
      { "tsql": "..."}   ← preferred
      { "sql": "..." }
      { "text": "..." } / { "query": "..." } / { "input": "..." }
    Or a text/plain body.
    """
    if isinstance(body, dict):
        for k in ("tsql", "sql", "text", "query", "input"):
            v = body.get(k)
            if isinstance(v, str) and v.strip():
                return v
    return (raw or "").strip()


# ---------- API: Convert ----------
@app.post("/api/convert", response_class=JSONResponse)
async def convert_api(request: Request):
    """
    Always respond 200 with:
      { "snowflake_sql": "<converted or -- Error: ...>" }
    so the frontend never shows a generic 'Conversion failed'.
    """
    body: Optional[dict] = None
    raw_text = ""
    try:
        body = await request.json()
    except Exception:
        try:
            raw_bytes = await request.body()
            raw_text = raw_bytes.decode("utf-8", errors="ignore")
        except Exception:
            pass

    tsql_text = _pick_text(body, raw_text)

    if not tsql_text:
        return JSONResponse({"snowflake_sql": "-- Error: No T-SQL provided"})

    batches = _split_batches(tsql_text)
    if not batches:
        return JSONResponse({"snowflake_sql": "-- Error: No statements found"})

    results: List[str] = []
    errors: List[str] = []

    for i, batch in enumerate(batches, start=1):
        try:
            snow = (tsql_to_snowflake(batch) or "").strip()
            results.append(f"-- Batch {i} (from GO)\n{snow}")
        except Exception as e:
            errors.append(str(e))
            results.append(f"-- Batch {i} skipped (invalid SQL): {batch[:50]}...")

    final_sql = "\n\n".join(results).strip()
    if errors:
        final_sql = f"-- One or more batches had errors: {' | '.join(errors)}\n\n" + final_sql

    return JSONResponse({"snowflake_sql": final_sql})
