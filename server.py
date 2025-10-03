# server.py
from fastapi import FastAPI
from pydantic import BaseModel
from converter import convert_text

app = FastAPI(title="SQL → Snowflake Bot", version="0.1.0")

class Payload(BaseModel):
    sql: str

@app.post("/convert")
def convert(payload: Payload):
    try:
        out = convert_text(payload.sql)
        return {"ok": True, "snowflake_sql": out}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.get("/health")
def health():
    return {"status": "ok"}
