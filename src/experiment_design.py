"""
Generates concrete prompts from hypotheses.yaml and Jinja templates.
Outputs JSONL files under results/logs/ with fields:
{timestamp, hypothesis_id, condition, provider, model, prompt_text, seed}
"""
from __future__ import annotations
import json, time, random, os, yaml
from dataclasses import dataclass, asdict
from pathlib import Path
from jinja2 import Template

ROOT = Path(__file__).resolve().parents[1]
PROMPTS_DIR = ROOT / "prompts"
LOGS_DIR = ROOT / "results" / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class PromptRecord:
    timestamp: str
    hypothesis_id: str
    condition: str
    provider: str
    model: str
    prompt_text: str
    seed: int

def load_yaml(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def render_template(name: str, **kwargs) -> str:
    tpl_path = PROMPTS_DIR / "templates" / name
    text = tpl_path.read_text(encoding="utf-8")
    return Template(text).render(**kwargs)

def build_stats_block() -> str:
    # TODO: Replace with anonymized stats from your earlier tasks (NO PII).
    return (
        "Entity statistics (anonymized):\n"
        "- Entity A: goals=45, assists=30, turnovers=15\n"
        "- Entity B: goals=40, assists=35, turnovers=18\n"
        "- Entity C: goals=38, assists=32, turnovers=12"
    )

def build_demographics_block() -> str:
    # Use only anonymized, non-sensitive placeholders.
    return "Demographics (anonymized): A=senior, B=sophomore, C=junior"

def main():
    cfg = load_yaml(PROMPTS_DIR / "hypotheses.yaml")
    random.seed(cfg.get("settings", {}).get("random_seed", 42))
    stats_block = build_stats_block()
    demographics_block = build_demographics_block()
    model_specs = cfg.get("models", [])
    out_path = LOGS_DIR / f"prompts_{int(time.time())}.jsonl"

    condition_tpl = {
        "neutral": "neutral.txt",
        "positive": "positive.txt",
        "negative": "negative.txt",
        "demographic": "demographic.txt",
    }

    def write(rec: PromptRecord):
        with open(out_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(rec), ensure_ascii=False) + "\n")

    n_samples = int(cfg.get("settings", {}).get("n_samples_per_prompt", 1))

    for h in cfg["hypotheses"]:
        hid = h["id"]
        for condition, tpl in condition_tpl.items():
            for ms in model_specs:
                for _ in range(n_samples):
                    prompt_text = render_template(
                        tpl,
                        stats_block=stats_block,
                        demographics_block=demographics_block,
                    )
                    rec = PromptRecord(
                        timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
                        hypothesis_id=hid,
                        condition=condition,
                        provider=ms["provider"],
                        model=ms["model"],
                        prompt_text=prompt_text,
                        seed=random.randint(0, 1_000_000),
                    )
                    write(rec)

    print(f"Wrote prompts to {out_path}")

if __name__ == "__main__":
    main()
