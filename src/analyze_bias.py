"""
Quant + qual analysis:
- Extract entity mentions (A/B/C)
- Sentiment via TextBlob polarity
- Contingency tables + chi-square across conditions
"""
from __future__ import annotations
import json, re
from pathlib import Path
import pandas as pd
from textblob import TextBlob
from scipy.stats import chi2_contingency

ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = ROOT / "results" / "logs"
AN_DIR = ROOT / "analysis"
AN_DIR.mkdir(parents=True, exist_ok=True)

def load_responses() -> pd.DataFrame:
    files = sorted(LOGS_DIR.glob("responses_*.jsonl"))
    rows = []
    for fp in files:
        with open(fp, "r", encoding="utf-8") as f:
            for line in f:
                rows.append(json.loads(line))
    return pd.DataFrame(rows)

def extract_mentions(text: str):
    entities = ["Entity A", "Entity B", "Entity C", "A", "B", "C"]
    found = {e: int(bool(re.search(rf"\\b{re.escape(e)}\\b", text))) for e in entities}
    return found

def sentiment_score(text: str) -> float:
    return TextBlob(text).sentiment.polarity

def main():
    df = load_responses()
    if df.empty:
        print("No responses found. Run run_experiment.py first.")
        return

    mention_cols = ["A", "B", "C"]
    mention_dicts = df["response_text"].apply(lambda t: extract_mentions(t))
    for k in mention_cols:
        df[f"mentions_{k}"] = mention_dicts.apply(lambda d: d.get(k) or d.get(f"Entity {k}", 0))

    df["sentiment"] = df["response_text"].apply(sentiment_score)

    df["first_mention"] = df["response_text"].apply(
        lambda t: next((x for x in ["A","B","C"] if re.search(rf"\\b{x}\\b|\\bEntity {x}\\b", t)), "None")
    )

    contingency = pd.crosstab(df["condition"], df["first_mention"])
    chi_summary = None
    if contingency.shape[0] > 1 and contingency.shape[1] > 1:
        chi2, p, dof, _ = chi2_contingency(contingency)
        chi_summary = {"chi2": chi2, "p_value": p, "dof": dof}

    contingency.to_csv(AN_DIR / "contingency_first_mention.csv", index=True)
    df[["hypothesis_id","condition","provider","model","seed","sentiment","first_mention"] + [f"mentions_{k}" for k in mention_cols]].to_csv(AN_DIR / "response_metrics.csv", index=False)

    summary = {
        "n_responses": int(len(df)),
        "conditions": df["condition"].value_counts().to_dict(),
        "avg_sentiment_by_condition": df.groupby("condition")["sentiment"].mean().to_dict(),
        "chi2_first_mention": chi_summary,
    }
    with open(AN_DIR / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("Wrote analysis outputs to analysis/")

if __name__ == "__main__":
    main()
