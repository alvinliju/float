import sqlite3, json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import agent

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def db():
    conn = sqlite3.connect("brain.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/health")
def health(): return {"ok": True}

@app.get("/merchants")
def merchants():
    conn = db()
    rows = conn.execute("SELECT * FROM merchants").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/merchants/{mid}/analyze")
def analyze(mid: int):
    conn = db()
    merchant    = dict(conn.execute("SELECT * FROM merchants WHERE id=?", (mid,)).fetchone())
    settlements = [dict(r) for r in conn.execute(
        "SELECT * FROM settlements WHERE merchant_id=? ORDER BY date DESC", (mid,)).fetchall()]
    tax_events  = [dict(r) for r in conn.execute(
        "SELECT * FROM tax_events WHERE merchant_id=?", (mid,)).fetchall()]
    conn.close()

    result = agent.analyze(merchant, settlements, tax_events)
    return {"merchant": merchant, "analysis": result}
