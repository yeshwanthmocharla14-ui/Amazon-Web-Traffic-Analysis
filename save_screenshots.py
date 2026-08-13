import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")
df = pd.read_csv("../data/amazon_traffic_raw.csv")
df["source"] = df["source"].astype(str).str.strip().str.title()

source_traffic = df["source"].value_counts(normalize=True).mul(100).round(1)
plt.figure(figsize=(8,5))
source_traffic.plot(kind="bar", color="#1F3864")
plt.title("Traffic Share by Source (%)")
plt.ylabel("% of Sessions")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("../screenshots/traffic_by_source.png", dpi=150)
plt.close()

conv_by_source = (df.groupby("source")["conversions"].mean() * 100).round(2).sort_values(ascending=False)
plt.figure(figsize=(8,5))
conv_by_source.plot(kind="bar", color="#2E7D32")
plt.title("Conversion Rate by Traffic Source (%)")
plt.ylabel("Conversion Rate (%)")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("../screenshots/conversion_by_source.png", dpi=150)
plt.close()

bounce_by_device = (df.groupby("device_category")["bounce_rate"].mean() * 100).round(1)
plt.figure(figsize=(6,5))
bounce_by_device.plot(kind="bar", color="#C0392B")
plt.title("Average Bounce Rate by Device (%)")
plt.ylabel("Bounce Rate (%)")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("../screenshots/bounce_rate_by_device.png", dpi=150)
plt.close()

print("Screenshots saved.")
