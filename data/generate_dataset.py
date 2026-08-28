"""Generate a synthetic, travel-themed customer-care ticket dataset.

This is the raw-input stage of the pipeline. In production the same shape of
data would land in BigQuery (see ../sql/queries.sql); here we emit a CSV so the
analysis (../analysis/analyze.py) is fully reproducible without cloud access.

Run:  python data/generate_dataset.py
Output: data/tickets.csv
"""
import csv
import os
import random
import datetime

SEED = 42
random.seed(SEED)

START = datetime.date(2026, 1, 1)
DAYS = 182  # ~6 months

CATEGORIES = {
    "Booking Change": 0.22,
    "Refund Request": 0.18,
    "Flight Delay":   0.16,
    "Baggage Issue":  0.12,
    "Cancellation":   0.10,
    "Complaint":      0.10,
    "Loyalty/Account":0.12,
}
# typical resolution time (hours) per category -> drives realism
BASE_RES = {
    "Booking Change": 6, "Refund Request": 30, "Flight Delay": 12,
    "Baggage Issue": 18, "Cancellation": 10, "Complaint": 24,
    "Loyalty/Account": 4,
}
CHANNELS = ["App", "Web", "Call Center", "Email", "WhatsApp"]
SEGMENTS = ["Leisure", "Business", "Corporate", "First-time"]
REGIONS  = ["Jakarta", "Surabaya", "Bali", "Medan", "Makassar"]
AGENTS   = [f"A{i:02d}" for i in range(1, 16)]


def generate(out_path: str) -> int:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    rows = []
    tid = 100000
    cats = list(CATEGORIES.keys())
    weights = list(CATEGORIES.values())
    for d in range(DAYS):
        date = START + datetime.timedelta(days=d)
        # gentle growth + weekend seasonality
        base = 22 + int(8 * (d / DAYS)) + (6 if date.weekday() >= 4 else 0)
        n = max(10, random.randint(base - 5, base + 8))
        for _ in range(n):
            tid += 1
            cat = random.choices(cats, weights=weights)[0]
            seg = random.choice(SEGMENTS)
            reg = random.choice(REGIONS)
            ch = random.choice(CHANNELS)
            agent = random.choice(AGENTS)
            br = BASE_RES[cat]
            res = max(0.5, round(random.gauss(br, br * 0.4), 1))
            resolved = random.random() > 0.06  # 6% still open
            if resolved:
                # CSAT falls as resolution time stretches past its category norm
                p5 = max(0.15, 0.82 - res / (br * 3.0))
                roll = random.random()
                if roll < p5:
                    csat = 5
                elif roll < p5 + 0.18:
                    csat = 4
                elif roll < p5 + 0.30:
                    csat = 3
                elif roll < p5 + 0.40:
                    csat = 2
                else:
                    csat = 1
                status = "Resolved"
            else:
                csat = ""
                status = "Open"
            rows.append([
                tid, date.isoformat(), ch, cat, seg, reg, agent,
                f"{res:.1f}", status, csat,
            ])
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "ticket_id", "created_date", "channel", "category",
            "customer_segment", "region", "agent", "resolution_hours",
            "status", "csat_score",
        ])
        w.writerows(rows)
    return len(rows)


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "tickets.csv")
    n = generate(out)
    print(f"wrote {n} tickets -> {out}")
