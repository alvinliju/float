"""
Pine Labs Plural API Client
============================
Direct REST calls to Plural UAT API.
MCP server returns docs, not execution — so we call the API directly.

Credentials in .env:
  PINELABS_CLIENT_ID
  PINELABS_CLIENT_SECRET
  PINELABS_BUSINESS_NAME
"""

import os, json, uuid, httpx
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BASE          = "https://pluraluat.v2.pinepg.in/api"
CLIENT_ID     = os.getenv("PINELABS_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("PINELABS_CLIENT_SECRET", "")
BUSINESS_NAME = os.getenv("PINELABS_BUSINESS_NAME", "")

DEMO_MODE = not (CLIENT_ID and CLIENT_SECRET)


def _get_token() -> str:
    r = httpx.post(
        f"{BASE}/auth/v1/token",
        json={
            "client_id":     CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type":    "client_credentials",
        },
        headers={
            "Content-Type":      "application/json",
            "Request-ID":        str(uuid.uuid4()),
            "Request-Timestamp": datetime.utcnow().isoformat() + "Z",
        },
        timeout=10,
    )
    print(f"[pinelabs] token status: {r.status_code}")
    r.raise_for_status()
    return r.json()["access_token"]


def get_settlements(from_date: str, to_date: str) -> list:
    if DEMO_MODE:
        print("[pinelabs] DEMO MODE — using seed data")
        return []

    try:
        token = _get_token()
        print(f"[pinelabs] token ok, fetching settlements {from_date} → {to_date}")

        r = httpx.get(
            f"{BASE}/settlements/v1/list",
            params={
                "start_date": from_date + "T00:00:00",
                "end_date":   to_date   + "T23:59:59",
                "page":       1,
            },
            headers={
                "Authorization":     f"Bearer {token}",
                "Request-ID":        str(uuid.uuid4()),
                "Request-Timestamp": datetime.utcnow().isoformat() + "Z",
            },
            timeout=10,
        )
        print(f"[pinelabs] settlements status: {r.status_code} | body: {r.text[:300]}")

        if r.status_code != 200:
            print("[pinelabs] non-200, falling back to seed data")
            return []

        data  = r.json()
        items = data if isinstance(data, list) else data.get("data", data.get("settlements", []))
        return [
            {
                "date":   item.get("settlement_date") or item.get("date", ""),
                "amount": float(item.get("settlement_amount") or item.get("amount", 0)),
            }
            for item in items
        ]

    except Exception as e:
        print(f"[pinelabs] error: {e} — falling back to seed data")
        return []
