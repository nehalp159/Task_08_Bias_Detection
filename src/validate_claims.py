"""
Validate response claims against ground-truth stats (placeholder).
Swap in your real anonymized summary table and parsing logic.
"""
from __future__ import annotations
import json, re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = ROOT / "results" / "logs"
AN_DIR = ROOT / "analysis"
AN_DIR.mkdir(parents=True, exist_ok=True)

def load_ground_truth() -> pd.DataFrame:
    # Replace with your dataset summary (anonymized).
    return pd.DataFrame([
        {"entity":"A", "goals":45, "assists":30, "turnovers":15},
        {"entity":"B", "goals":40, "assists":35, "turnovers":18},
        {"entity":"C", "goals":38, "assists":32, "turnovers":12},
    ])

def check_fabrication(response: str, truth: pd.DataFrame) -> dict:
    fabricated = False
    matches = re.findall(r"(\\d+)\\s+(goals|assists|turnovers)", response.lower())
    for num, stat in matches:
        if int(num) > 100:  # simple heuristic
            fabricated = True
            break
    return {"fabricated": fabricated, "notes": "Heuristic check; extend with parsing of claims vs truth."}

def main():
    truth = load_ground_truth()
    files = sorted(LOGS_DIR.glob("responses_*.jsonl"))
    out_rows = []
    for fp in files:
        for line in fp.read_text(encoding="utf-8").splitlines():
            rec = json.loads(line)
            out = check_fabrication(rec["response_text"], truth)
            out.update({k: rec[k] for k in ["hypothesis_id","condition","provider","model","seed"]})
            out_rows.append(out)
    pd.DataFrame(out_rows).to_csv(AN_DIR / "fabrication_checks.csv", index=False)
    print("Wrote validation outputs to analysis/fabrication_checks.csv")

if __name__ == "__main__":
    main()
