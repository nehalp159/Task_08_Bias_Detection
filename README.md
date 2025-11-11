# Task 08 – Bias Detection in LLM Data Narratives

---

## Author
**Nehal Pawar**  
October-November 2025

---

## Project Description
This research explores whether large language models (LLMs) generate **biased narratives** when describing identical datasets under different framings.
By adding a controlled test that examines the impacts of framing and demographics on generated summaries, it expands on earlier data-analysis work.

---

## Objectives
- Analyze narratives produced by LLM for tone or framing bias.  
- Calculate how subject focus and sentiment change depending on the prompt conditions.  
- Determine whether demographic references alter the statements tone.  
- Verify factual clarity and identify false information.

---

## Dataset / Input
- The dataset used is an **anonymized statistical summary** (e.g., Entity A/B/C with numeric metrics).  
- The repository contains no source data or personally identifiable information (PII). 
- All raw datasets are excluded via `.gitignore`.

---

## Methodology
1. **Prompt Generation:** Controlled templates for demographic, positive, negative, and neutral framings.  
2. **Experiment Execution:** Every prompt was sent to a simulated or API-based LLM to produce narratives.  
3. **Analysis:** TextBlob sentiment scoring, entity-mention frequency, and fabrication detection.  
4. **Visualization:** Using Matplotlib, sentiment and first-mention distributions.  
5. **Validation:** Cross-check for implausible claims and summarize in `fabrication_checks.csv`.

---

## Project Structure
```
Task_08_Bias_Detection/
├── .gitignore
├── README.md                  
├── requirements.txt                  
├── prompts/
│   ├── hypotheses.yaml
│   └── templates/
│       ├── neutral.txt
│       ├── positive.txt
│       ├── negative.txt
│       └── demographic.txt
├── src/
│   ├── experiment_design.py        # Generates controlled prompts
│   ├── run_experiment.py           # Executes prompt–response collection
│   ├── analyze_bias.py             # Computes sentiment and first-mention metrics
│   └── validate_claims.py          # Detects and logs factual inconsistencies
├── analysis/
│   ├── summary.json                # Overall metrics summary
│   ├── make_plots.py               # Generates visualizations
│   ├── figures/
│       ├── avg_sentiment_by_condition.png
│       └── first_mention_distribution.png
│   ├── summary_tables/
│       └── bias_summary.csv
├── reports/
│   └── REPORT.md                   # Final narrative and interpretation
└── results/
    └── logs/                       # JSONL prompt–response logs (no raw data)
```

---

## Requirements
- pandas
- matplotlib
- textblob
- numpy
- scipy
- jsonlines
- tqdm
- requests
- python-dotenv

## Installation Instructions
1. Clone the repository:
git clone https://github.com/yourusername/Task_08_Bias_Detection.git
cd Task_08_Bias_Detection

2. Create & activate a virtual environment:
python -m venv venv
source venv/bin/activate   # macOS / Linux
venv\Scripts\activate      # Windows

3. Install dependencies:
pip install -r requirements.txt

## How to Reproduce
1. Generate prompts:
python -m src.experiment_design

2. Run experiment (simulated by default):
python -m src.run_experiment

3. Analyze bias & validate claims:
python -m src.analyze_bias
python -m src.validate_claims

4. Produce figures & tables:
python analysis/make_plots.py

## Key Findings
- Average sentiment differs across framings:
Demographic ≈ −0.19,
Neutral ≈ −0.15,
Negative ≈ −0.13,
Positive ≈ −0.05
- Overall, demographic priming generated the most negative tone.
- Chi-square N/A indicates no statistically significant preference in the first-mentioned - entity.
- No sign of systematic deception.

## Results / Artifacts
- analysis/figures/avg_sentiment_by_condition.png
- analysis/figures/first_mention_distribution.png
- analysis/summary_tables/bias_summary.csv
- reports/REPORT.md

## Ethics & Disclosure
- All information (Entities A/B/C) is anonymised.
- PII and real-world subjects are excluded.
- In line with GitHub and IRB guidelines, all raw datasets are excluded.

## Challenges Encountered
- Aligning the prompt tone without letting "neutral" and "negative" overlap.
- Stopping the leakage of untracked data while making GitHub commits.
- Managing sentiment polarity mismatches during simulated runs.

## Future Improvements
- Use live LLM APIs (Gemini, Anthropic, OpenAI).
- Add measurements for bias-classifiers and toxicity.
- For qualitative bias coding, add human annotation.
- Automate comparisons between models.

## Overall Conclusion
Subtle bias is confirmed by the measurable impact of framing & demographic references on the mood of LLM-generated narratives.
This framework offers controlled bias-auditing experiments a reproducible base.

## Contact
For inquiries about this analysis, please contact: nepawar@syr.edu

## Acknowledgments
Under Professor Jonathan's guidance, the project completed as part of Syracuse University's research requirements.