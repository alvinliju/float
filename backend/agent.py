import json, anthropic
from dotenv import load_dotenv
load_dotenv()

client = anthropic.AnthropicBedrock()

SYSTEM = """You are a CFO agent for a payments company. You analyze merchant POS settlement data
and identify cash flow risks. Output JSON only, no markdown, no preamble.

Schema:
{
  "health_score": 0-100,
  "trend": "growing|stable|declining",
  "gap_detected": true|false,
  "gap_amount": number,
  "days_until_crisis": number,
  "diagnosis": "2-3 sentences for credit officer, plain english, facts only",
  "recommend_offer": true|false,
  "suggested_amount": number,
  "confidence": "high|medium|low"
}"""

def analyze(merchant: dict, settlements: list, tax_events: list) -> dict:
    s_text = "\n".join(f"  {s['date']}: ₹{s['amount']:,.0f}" for s in settlements[-30:])
    t_text = "\n".join(f"  {t['event_type']} due {t['due_date']}: ₹{t['estimated_amount']:,.0f}"
                       for t in tax_events) or "  None"

    resp = client.messages.create(
        model      = "us.anthropic.claude-3-5-haiku-20241022-v1:0",
        max_tokens = 400,
        system     = SYSTEM,
        messages   = [{"role": "user", "content": f"""
Merchant: {merchant['name']}, {merchant['category']}, {merchant['location']}
Monthly GMV: ₹{merchant['monthly_gmv']:,.0f}

Settlements (last 30 days, newest first):
{s_text}

Tax events:
{t_text}

Today: {__import__('datetime').date.today()}
"""}]
    )

    raw = resp.content[0].text.strip().strip("```json").strip("```")
    return json.loads(raw)
