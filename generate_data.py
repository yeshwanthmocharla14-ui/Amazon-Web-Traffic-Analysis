"""
Generates a synthetic Amazon-style website traffic dataset matching the
columns documented in the project README.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(11)
N = 42815

sources = ["Organic Search", "Direct", "Paid Search", "Social", "Referral", "Email"]
source_probs = [0.32, 0.22, 0.18, 0.14, 0.09, 0.05]
# conversion + bounce behaviour differs by source
source_conv_rate = {"Organic Search": 0.035, "Direct": 0.05, "Paid Search": 0.045,
                     "Social": 0.02, "Referral": 0.03, "Email": 0.06}
source_bounce_base = {"Organic Search": 0.42, "Direct": 0.35, "Paid Search": 0.48,
                       "Social": 0.58, "Referral": 0.40, "Email": 0.33}

devices = ["Mobile", "Desktop", "Tablet"]
device_probs = [0.58, 0.35, 0.07]
device_bounce_adj = {"Mobile": 0.06, "Desktop": -0.05, "Tablet": 0.02}

countries = ["United States", "India", "United Kingdom", "Canada", "Germany",
             "Australia", "Brazil", "France", "Japan", "Mexico", "Other"]
country_probs = [0.30, 0.18, 0.09, 0.07, 0.06, 0.05, 0.05, 0.04, 0.04, 0.04, 0.08]

page_paths = ["/home", "/deals", "/product/electronics", "/product/fashion",
              "/product/home-kitchen", "/cart", "/checkout", "/search",
              "/account", "/product/books"]
page_probs = [0.22, 0.14, 0.16, 0.13, 0.10, 0.08, 0.05, 0.07, 0.03, 0.02]

start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 12, 31)
date_range_seconds = int((end_date - start_date).total_seconds())

rows = []
for i in range(N):
    source = np.random.choice(sources, p=source_probs)
    device = np.random.choice(devices, p=device_probs)
    country = np.random.choice(countries, p=country_probs)
    page = np.random.choice(page_paths, p=page_probs)

    bounce_rate = np.clip(
        np.random.normal(source_bounce_base[source] + device_bounce_adj[device], 0.08), 0.05, 0.95
    )
    session_duration = max(3, np.random.gamma(shape=2.0, scale=90 * (1 - bounce_rate + 0.3)))

    page_views = max(1, int(np.random.poisson(3 if bounce_rate < 0.4 else 1)))
    unique_page_views = max(1, int(page_views * np.random.uniform(0.6, 1.0)))

    is_new_user = np.random.rand() < 0.62
    converted = np.random.rand() < source_conv_rate[source] * (1.4 if device == "Desktop" else 1.0)

    ts = start_date + timedelta(seconds=int(np.random.randint(0, date_range_seconds)))

    rows.append({
        "session_id": f"SESS-{300000 + i}",
        "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
        "country": country,
        "device_category": device,
        "source": source,
        "page_path": page,
        "avg_session_duration_sec": round(session_duration, 1),
        "bounce_rate": round(bounce_rate, 3),
        "conversions": int(converted),
        "new_user": "Yes" if is_new_user else "No",
        "page_views": page_views,
        "unique_page_views": unique_page_views,
    })

df = pd.DataFrame(rows)

# ~10% missing/inconsistent entries to mirror a real raw export
missing_idx = np.random.choice(df.index, size=int(0.10 * len(df)), replace=False)
half = len(missing_idx) // 2
for idx in missing_idx[:half]:
    col = np.random.choice(["avg_session_duration_sec", "bounce_rate", "device_category"])
    df.loc[idx, col] = np.nan
for idx in missing_idx[half:]:
    df.loc[idx, "source"] = df.loc[idx, "source"].lower() + "  "

df.to_csv("/home/claude/proj4_amazon_traffic/data/amazon_traffic_raw.csv", index=False)

# sanity checks
clean = df.copy()
clean["source"] = clean["source"].astype(str).str.strip().str.title()
print("Rows:", len(df))
print("\nTraffic share by source (%):")
print((clean["source"].value_counts(normalize=True) * 100).round(1))
print("\nConversion rate by source (%):")
print((clean.groupby("source")["conversions"].mean() * 100).round(2).sort_values(ascending=False))
print("\nBounce rate by device (%):")
print((clean.groupby("device_category")["bounce_rate"].mean() * 100).round(1))
print("\nNew vs returning users:")
print(clean["new_user"].value_counts(normalize=True).round(2))
