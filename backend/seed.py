import sqlite3, random, json
from datetime import date, timedelta

random.seed(42)
today = date.today()

conn = sqlite3.connect("brain.db")
conn.executescript("""
DROP TABLE IF EXISTS settlements;
DROP TABLE IF EXISTS tax_events;
DROP TABLE IF EXISTS merchants;

CREATE TABLE merchants (
    id          INTEGER PRIMARY KEY,
    name        TEXT,
    location    TEXT,
    category    TEXT,
    monthly_gmv REAL
);

CREATE TABLE settlements (
    id          INTEGER PRIMARY KEY,
    merchant_id INTEGER,
    date        TEXT,
    amount      REAL
);

CREATE TABLE tax_events (
    id               INTEGER PRIMARY KEY,
    merchant_id      INTEGER,
    event_type       TEXT,
    due_date         TEXT,
    estimated_amount REAL
);
""")

MERCHANTS = [
    ("Sharma Medical Store", "Dharavi, Mumbai",   "pharmacy",   800000,  26667, 0.08, [("GST_QUARTERLY", 6,  220000)]),
    ("Anand Tiffin Centre",  "Bandra, Mumbai",    "restaurant", 300000,  10000, 0.25, []),
    ("Krishna Electronics",  "Pune",              "retail",     1200000, 40000, 0.15, [("ADVANCE_TAX",  18,  90000)]),
    ("Priya Kirana Mart",    "Chennai",           "grocery",    500000,  16667, 0.10, [("TDS",           4,  80000)]),
    ("Raj Tailors",          "Karol Bagh, Delhi", "apparel",    200000,  6667,  0.35, [("GST_QUARTERLY", 9,  45000)]),
]

for i, (name, loc, cat, gmv, daily_avg, var, taxes) in enumerate(MERCHANTS, 1):
    conn.execute("INSERT INTO merchants VALUES (?,?,?,?,?)", (i, name, loc, cat, gmv))

    trend = 1.015 if name == "Krishna Electronics" else 0.985 if name == "Raj Tailors" else 1.0
    for offset in range(30, 0, -1):
        day    = today - timedelta(days=offset)
        amount = daily_avg * (trend ** (30 - offset)) * random.gauss(1.0, var)
        if cat == "restaurant" and day.weekday() in (4, 5, 6):
            amount *= 1.5
        conn.execute("INSERT INTO settlements (merchant_id,date,amount) VALUES (?,?,?)",
                     (i, day.isoformat(), round(max(amount, 500), 2)))

    for ev_type, days_ahead, amount in taxes:
        conn.execute("INSERT INTO tax_events (merchant_id,event_type,due_date,estimated_amount) VALUES (?,?,?,?)",
                     (i, ev_type, (today + timedelta(days=days_ahead)).isoformat(), amount))

conn.commit()
conn.close()
print("Seeded brain.db — 5 merchants, 30 days settlements, tax events")
