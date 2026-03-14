"""
Pine Labs MCP Client
====================
Connects to the hosted Pine Labs SSE MCP server.
Fetches settlements for one merchant and returns them
in the same shape our agent.py expects.

Credentials go in .env:
  PINELABS_CLIENT_ID=...
  PINELABS_CLIENT_SECRET=...
  PINELABS_BUSINESS_NAME=...
"""

import os, json, asyncio
from dotenv import load_dotenv
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

load_dotenv()

MCP_URL       = "https://mcp.pinelabs.com/sse"
CLIENT_ID     = os.getenv("PINELABS_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("PINELABS_CLIENT_SECRET", "")
BUSINESS_NAME = os.getenv("PINELABS_BUSINESS_NAME", "")

DEMO_MODE = not (CLIENT_ID and CLIENT_SECRET and BUSINESS_NAME)


async def _fetch_settlements_async(from_date: str, to_date: str) -> dict:
    headers = {"x-business-name": BUSINESS_NAME}

    async with sse_client(MCP_URL, headers=headers) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Step 1: get auth token
            token_resp = await session.call_tool("generate_token", {
                "client_id":     CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            })
            token_data = json.loads(token_resp.content[0].text)
            token = token_data.get("access_token") or token_data.get("token")

            # Step 2: fetch settlements
            settlements_resp = await session.call_tool("get_all_settlements", {
                "access_token": token,
                "from_date":    from_date,
                "to_date":      to_date,
            })
            return json.loads(settlements_resp.content[0].text)


def get_settlements(from_date: str, to_date: str) -> list:
    """
    Returns list of { date, amount } dicts from Pine Labs.
    Falls back to empty list in demo mode (seed.py data used instead).
    """
    if DEMO_MODE:
        print("[pinelabs_mcp] DEMO MODE — no credentials, using seed data")
        return []

    raw = asyncio.run(_fetch_settlements_async(from_date, to_date))

    # Normalize Pine Labs response → our shape
    items = raw if isinstance(raw, list) else raw.get("data", raw.get("settlements", []))
    return [
        {
            "date":   item.get("settlement_date") or item.get("date", ""),
            "amount": float(item.get("settlement_amount") or item.get("amount", 0)),
        }
        for item in items
        if item.get("settlement_amount") or item.get("amount")
    ]
