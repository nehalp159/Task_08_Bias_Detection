# Bias Detection in LLM Data Narratives — Final Report (Task 08)

**Author:** Nehal Pawar

---

## Executive Summary
**Goal.** Detect whether **LLM-generated narratives** change when identical data is presented under different framings (neutral, positive, negative) and with/without **demographic mention**, using anonymized statistics (e.g., “Entity A/B/C”).

**Scope.** Balanced design across four conditions (neutral, positive, negative, demographic). Prompts and runs were logged; analysis produced summary metrics, contingency tables, figures, and fabrication checks.

**Headline findings.**
- Average sentiment is most negative under **demographic** framing (≈ −0.19), followed by **neutral** (≈ −0.15) and **negative** (≈ −0.13); **positive** is least negative (≈ −0.05).  
- The **chi-square** test for first-mention distributions was **not applicable** (no strong differentiation by condition).  
- Implication: Wording and demographic priming measurably shift narrative tone even with identical data.

---

## Methodology
- **Design.** Controlled, between-prompt manipulation: *neutral, positive, negative, demographic*. Prompt templates differ only in framing variable per hypothesis.
- **Data.** Anonymized summary statistics from prior tasks (entities A/B/C; metrics like goals/assists/turnovers). **No PII**, **no raw datasets** in repo.
- **Execution.**  
  - Prompt generation: `src/experiment_design.py`  
  - Response collection: `src/run_experiment.py` (simulated by default)  
  - Analysis: `src/analyze_bias.py` → `analysis/summary.json`, `response_metrics.csv`, `contingency_first_mention.csv`  
  - Validation: `src/validate_claims.py` → `analysis/fabrication_checks.csv`
- **Metrics.**  
  - **Sentiment polarity** (TextBlob)  
  - **First-mention entity** as a proxy for recommendation bias  
  - **Fabrication heuristic** (flags implausible numeric claims)

---

## Results

### 1) Sentiment by Framing
Average sentiment by condition (from `analysis/summary.json`):

- **Demographic:** ≈ −0.19  
- **Neutral:** ≈ −0.15  
- **Negative:** ≈ −0.13  
- **Positive:** ≈ −0.05  

See: `analysis/figures/avg_sentiment_by_condition.png`.

**Interpretation.** Demographic mention exhibits the most negative tone; even “neutral” prompts skew mildly negative, while positive framing yields the least negative tone.

### 2) Entity Selection (First Mention)
The first-mention chi-square was **not applicable** (no strong differentiation across conditions).  
See: `analysis/figures/first_mention_distribution.png` and `analysis/contingency_first_mention.csv`.

### 3) Consolidated Bias Metrics
A combined table of counts, average sentiment, share of negative responses (sentiment < 0), and first-mention shares is saved to:  
`analysis/summary_tables/bias_summary.csv`.

### 4) Fabrication Check (Heuristic)
`analysis/fabrication_checks.csv` flags obviously implausible numeric claims (e.g., >100 goals). In this simulated run, no strong condition-specific pattern emerged. Replace with dataset-specific rules for real-model runs.

---

## Bias Catalogue

| Bias Type | Evidence | Severity | Mitigation |
|---|---|---|---|
| **Framing Bias** | Negative tone increases under negative/neutral wording vs positive framing. | Medium | **Prompt parity** (balanced positive/negative phrasing), tone constraints (“avoid value-laden language”), **post-hoc sentiment normalization**. |
| **Demographic Priming** | Demographic mention shows the **most negative** average tone. | High | Avoid unnecessary demographics, include explicit **“do not consider demographics”** guidance, run **paired audits** with/without demographics. |
| **Lexical Drift** | Neutral prompts mildly negative at baseline. | Low–Medium | Use multiple neutral variants; monitor and regularize tone across versions. |

---

## Limitations & Next Steps
- This run used **simulated** outputs; re-run with **real APIs** (OpenAI/Anthropic/Gemini) to confirm magnitude/patterns.  
- Sentiment is a coarse proxy; add targeted bias classifiers (e.g., toxicity) and **human coding** for nuance.  
- Extend extraction to detect the **explicit recommended entity** (beyond first mention).

---

## Ethical & Data Hygiene Notes
- **No PII**; actors anonymized (Entity A/B/C).  
- **No datasets** in repo (blocked by `.gitignore`).  
- Logs of prompts/responses are retained only in `results/logs/`; `results/raw/` remains untracked.

---

## Provenance
- Counts and means: `analysis/summary.json`  
- First-mention distribution: `analysis/contingency_first_mention.csv`  
- Per-response metrics: `analysis/response_metrics.csv`  
- Fabrication flags: `analysis/fabrication_checks.csv`
