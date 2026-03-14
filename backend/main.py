import sqlite3, json
from datetime import date, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import agent, pinelabs_mcp

app = FastAPI(title="Settlement Brain")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def db():
    conn = sqlite3.connect("brain.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/health")
def health():
    return {"ok": True, "mcp_mode": not pinelabs_mcp.DEMO_MODE}


@app.get("/merchants")
def merchants():
    rows = db().execute("SELECT * FROM merchants").fetchall()
    return [dict(r) for r in rows]


@app.get("/merchants/{mid}/analyze")
def analyze(mid: int):
    conn = db()
    merchant = conn.execute("SELECT * FROM merchants WHERE id=?", (mid,)).fetchone()
    if not merchant:
        raise HTTPException(404, "Merchant not found")
    merchant = dict(merchant)

    tax_events = [dict(r) for r in conn.execute(
        "SELECT * FROM tax_events WHERE merchant_id=?", (mid,)).fetchall()]

    # Try Pine Labs MCP first — real settlement data
    from_date = (date.today() - timedelta(days=30)).isoformat()
    to_date   = date.today().isoformat()
    settlements = pinelabs_mcp.get_settlements(from_date, to_date)

    # Fall back to seed DB if MCP returned nothing
    if not settlements:
        rows = conn.execute(
            "SELECT date, amount FROM settlements WHERE merchant_id=? ORDER BY date DESC",
            (mid,)
        ).fetchall()
        settlements = [dict(r) for r in rows]

    conn.close()

    result = agent.analyze(merchant, settlements, tax_events)
    return {
        "merchant":    merchant,
        "analysis":    result,
        "data_source": "pinelabs_mcp" if not pinelabs_mcp.DEMO_MODE else "seed_db",
    }
