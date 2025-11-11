# analysis/make_plots.py
# Generates figures and a consolidated summary table from analysis outputs.
# Usage:
#   python analysis/make_plots.py

from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt  # Do not set custom styles/colors

ROOT = Path(__file__).resolve().parents[0]
FIG_DIR = ROOT / "figures"
TAB_DIR = ROOT / "summary_tables"
FIG_DIR.mkdir(parents=True, exist_ok=True)
TAB_DIR.mkdir(parents=True, exist_ok=True)

# ---- Load inputs produced by src.analyze_bias.py / validate_claims.py ----
summary = json.loads((ROOT / "summary.json").read_text(encoding="utf-8"))
cont = pd.read_csv(ROOT / "contingency_first_mention.csv")
resp = pd.read_csv(ROOT / "response_metrics.csv")
fabric = pd.read_csv(ROOT / "fabrication_checks.csv")

# Ensure required columns exist
required_cols = {"condition", "sentiment", "first_mention", "seed"}
missing = required_cols - set(resp.columns)
if missing:
    raise ValueError(f"Missing columns in response_metrics.csv: {missing}")

# ---- Build consolidated summary table robustly ----
# Establish canonical condition order from the response data
cond_order = sorted(resp["condition"].dropna().unique().tolist())

# Base frame with one row per condition
base = pd.DataFrame({"condition": cond_order}).set_index("condition")

# n_responses per condition
n_by_cond = resp.groupby("condition")["seed"].count().reindex(cond_order)
base["n_responses"] = n_by_cond.values

# average sentiment per condition
avg_sent = resp.groupby("condition")["sentiment"].mean().reindex(cond_order)
base["avg_sentiment"] = avg_sent.values

# share of negative sentiment (<0) per condition
neg_rate = (resp.assign(is_negative=(resp["sentiment"] < 0).astype(int))
                .groupby("condition")["is_negative"]
                .mean()
                .reindex(cond_order))
base["share_negative"] = neg_rate.values

# first-mention distribution per condition → proportions
fm_ct = pd.crosstab(resp["condition"], resp["first_mention"]).reindex(cond_order).fillna(0)
row_sums = fm_ct.sum(axis=1).replace(0, 1)
fm_pct = fm_ct.div(row_sums, axis=0)

# Prefix columns and join
fm_pct = fm_pct.add_prefix("share_first_")
bias_summary = base.join(fm_pct, how="left").reset_index()

# Save summary table
TAB_DIR.mkdir(parents=True, exist_ok=True)
(bias_summary.sort_values("condition")).to_csv(TAB_DIR / "bias_summary.csv", index=False)

# ---- Figures ----

# 1) Average sentiment by framing (from summary.json to ensure consistency with earlier pipeline)
avg_sentiment = pd.Series(summary["avg_sentiment_by_condition"])
plt.figure()
avg_sentiment.reindex(sorted(avg_sentiment.index)).plot(kind="bar", rot=0)
plt.title("Average Sentiment by Framing Condition")
plt.ylabel("Polarity (TextBlob)")
plt.xlabel("Condition")
plt.tight_layout()
plt.savefig(FIG_DIR / "avg_sentiment_by_condition.png")
plt.close()

# 2) First-mention distribution (stacked bar) from contingency_first_mention.csv
# Ensure condition is the index
cont = cont.rename(columns={cont.columns[0]: "condition"}).set_index("condition")
cont = cont.reindex(cond_order).fillna(0)
row_sums2 = cont.sum(axis=1).replace(0, 1)
cont_pct = cont.div(row_sums2, axis=0)

plt.figure()
bottom = None
for col in cont_pct.columns:
    vals = cont_pct[col].values
    if bottom is None:
        plt.bar(cont_pct.index, vals, label=col)
        bottom = vals
    else:
        plt.bar(cont_pct.index, vals, bottom=bottom, label=col)
        bottom = bottom + vals
plt.title("First-Mention Distribution by Condition")
plt.ylabel("Proportion")
plt.xlabel("Condition")
plt.legend()
plt.tight_layout()
plt.savefig(FIG_DIR / "first_mention_distribution.png")
plt.close()

print("✅ Wrote figures to analysis/figures/ and summary table to analysis/summary_tables/bias_summary.csv")
