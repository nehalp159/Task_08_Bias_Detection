"""
Executes LLM queries for each prompt in results/logs/*.jsonl
Writes raw model outputs under results/raw/ (gitignored) and a compact JSONL under results/logs/
"""
from __future__ import annotations
import json, time, random, os
from pathlib import Path
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = ROOT / "results" / "logs"
RAW_DIR = ROOT / "results" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv()
USE_REAL_API = os.getenv("USE_REAL_API", "0") == "1"

# Lazy imports only if needed
def _lazy_imports():
    clients = {}
    if USE_REAL_API:
        try:
            import openai
            clients["openai"] = openai
        except Exception:
            pass
        try:
            import anthropic
            clients["anthropic"] = anthropic
        except Exception:
            pass
        try:
            import google.generativeai as genai
            clients["google"] = genai
        except Exception:
            pass
    return clients

@dataclass
class OutputRecord:
    timestamp: str
    hypothesis_id: str
    condition: str
    provider: str
    model: str
    seed: int
    prompt_text: str
    response_text: str

def iter_prompt_logs():
    for p in sorted(LOGS_DIR.glob("prompts_*.jsonl")):
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                yield json.loads(line)

def call_model(provider: str, model: str, prompt: str, seed: int) -> str:
    if not USE_REAL_API:
        random.seed(seed)
        return f"[SIMULATED-{provider}/{model}] Seed={seed}\nPrompt:\n{prompt}\n\nResponse: (simulated text)\n"

    clients = _lazy_imports()
    if provider == "openai" and "openai" in clients:
        # Minimal example; adjust per your installed openai SDK version.
        import openai
        openai.api_key = os.getenv("OPENAI_API_KEY", "")
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=float(os.getenv("TEMPERATURE", "0.2")),
            n=1,
        )
        return resp.choices[0].message["content"]

    if provider == "anthropic" and "anthropic" in clients:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
        msg = client.messages.create(
            model=model,
            max_tokens=800,
            temperature=float(os.getenv("TEMPERATURE", "0.2")),
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join([blk.text for blk in msg.content])

    if provider == "google" and "google" in clients:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY", ""))
        m = genai.GenerativeModel(model)
        r = m.generate_content(prompt)
        return r.text or ""

    # Fallback to simulation if SDK not available
    random.seed(seed)
    return f"[SIMULATED-{provider}/{model}] Seed={seed}\nPrompt:\n{prompt}\n\nResponse: (simulated text)\n"

def main():
    out_path = LOGS_DIR / f"responses_{int(time.time())}.jsonl"
    for rec in iter_prompt_logs():
        text = call_model(rec["provider"], rec["model"], rec["prompt_text"], rec["seed"])
        raw_file = RAW_DIR / f'{rec["hypothesis_id"]}_{rec["condition"]}_{rec["provider"]}_{rec["model"]}_{rec["seed"]}.txt'
        raw_file.write_text(text, encoding="utf-8")

        out = OutputRecord(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            hypothesis_id=rec["hypothesis_id"],
            condition=rec["condition"],
            provider=rec["provider"],
            model=rec["model"],
            seed=rec["seed"],
            prompt_text=rec["prompt_text"],
            response_text=text[:4000]
        )
        with open(out_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(out), ensure_ascii=False) + "\n")

    print(f"Wrote responses to {out_path} and raw txt files to {RAW_DIR}")

if __name__ == "__main__":
    main()
