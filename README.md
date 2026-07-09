# Resume Screening Agent

A working AI agent that ranks a set of resumes against a job description
and outputs a scored, ordered shortlist with reasoning for each candidate.

Built for the Rooman Technologies 24-Hour AI Agent Challenge
(Junior AI Research Associate — Selection Round).

> **My agent takes** a job description + a folder of resumes (PDF/DOCX/TXT)
> **and produces** a ranked, scored shortlist (CSV + JSON) with a
> human-readable explanation of why each candidate ranked where they did.

---

## 1. What this agent does

```
Job description  ─┐
                   ├─► Parse ─► Extract (skills/education/experience) ─► Score ─► Rank ─► CSV/JSON + console shortlist
Resumes (PDF/      ┘
DOCX/TXT)
```

1. **Parses** resumes in PDF, DOCX, or plain text format into raw text.
2. **Extracts** structured fields from each resume and from the job
   description: skills, education level, years of experience, name,
   email, phone.
3. **Scores** every resume against the JD using a weighted blend of:
   - TF-IDF cosine similarity (semantic overlap of the full text)
   - Skill overlap (required skills found vs. missing)
   - Years-of-experience match
4. **Ranks** candidates highest score first and tiers them
   (`Strong Match` / `Possible Match` / `Weak Match`).
5. **Outputs** a console shortlist plus `ranked_candidates.csv` and
   `ranked_candidates.json` in `output/`.

This agent runs **fully offline** — no LLM API key is required. See
[§6 Design tradeoffs](#6-design-tradeoffs-and-what-id-improve) for why,
and how an LLM/embeddings layer would be added on top.

---

## 2. Project structure

```
resume-screening-agent/
│
├── src/
│   ├── main.py          # CLI entry point — wires the pipeline together
│   ├── parser.py        # Reads PDF / DOCX / TXT resumes into raw text
│   ├── extractor.py     # Extracts skills, education, experience, contact info
│   ├── similarity.py    # TF-IDF + cosine similarity (JD vs. resumes)
│   ├── scorer.py        # Combines similarity + skills + experience into a score
│   ├── exporter.py      # Writes ranked results to CSV and JSON
│   ├── utils.py         # Text cleaning, regex helpers, logging
│   └── config.py        # Weights, skill taxonomy, paths, thresholds
│
├── data/
│   ├── job_description/jd.txt      # Sample JD (Machine Learning Engineer)
│   └── resumes/                    # 13 sample resumes (.txt, .docx, .pdf)
│
├── output/
│   ├── ranked_candidates.csv       # Generated on each run
│   └── ranked_candidates.json      # Generated on each run
│
├── tests/
│   ├── conftest.py
│   └── test_pipeline.py            # 9 unit tests covering extraction & scoring
│
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

---

## 3. Setup

### Prerequisites
- Python 3.9+
- pip

### Install

```bash
git clone <your-repo-url>
cd resume-screening-agent
pip install -r requirements.txt
```

No API keys, no accounts, no environment variables needed — this agent
does not call any external LLM API. (If you want to extend it with one,
see [§6](#6-design-tradeoffs-and-what-id-improve).)

---

## 4. How to run it

Run against the bundled sample JD and resumes:

```bash
python src/main.py
```

This will:
- Load `data/job_description/jd.txt` (auto-detected if `--jd` is omitted)
- Load every resume in `data/resumes/` (`.pdf`, `.docx`, `.txt`)
- Print the top 5 candidates to the console
- Write the full ranked list to `output/ranked_candidates.csv` and
  `output/ranked_candidates.json`

### Custom run

```bash
python src/main.py \
  --jd path/to/your_job_description.pdf \
  --resumes path/to/your/resumes_folder \
  --top 10 \
  --out-prefix my_run
```

| Flag           | Default                       | Description                                  |
|----------------|--------------------------------|-----------------------------------------------|
| `--jd`         | first file in `data/job_description/` | Path to a JD file (PDF/DOCX/TXT)        |
| `--resumes`    | `data/resumes/`                | Folder of resumes to screen                   |
| `--top`        | `5`                             | How many top candidates to print to console  |
| `--out-prefix` | `ranked_candidates`             | Filename prefix for the CSV/JSON output       |

### Run the tests

```bash
python -m pytest tests/ -v
```

9 tests cover skill extraction (including negation handling), education
level detection, experience parsing, and the end-to-end scoring/ranking
logic.

---

## 5. Sample output

Bundled sample data: 1 JD (`Machine Learning Engineer`) and 13 resumes
of varying fit (from strong senior ML engineers to a marketing analyst
with no technical overlap), across `.txt`, `.docx`, and `.pdf` to prove
multi-format parsing.

Console output (truncated to top 3):

```
==============================================================================
RESUME SCREENING RESULTS — Top 5 of 13 candidates
==============================================================================

#1  Neha Kapoor  —  55.2/100  [Possible Match]
    File: resume_11_neha.txt
    Email: neha.kapoor@email.com
    Education: Master  |  Experience: 7 yrs
    Reasoning: Matches 16 required skill(s): aws, azure, docker, kubernetes,
    large language models, machine learning, nlp, numpy, pandas, prompt
    engineering, python, pytorch, rag, scikit-learn, sql, tensorflow.
    Missing: data analysis, data science, gcp, retrieval augmented generation.
    Semantic similarity to JD: 16%. Experience: 7 yrs vs 3 yrs required (100%).

#2  Ananya Sharma  —  51.85/100  [Possible Match]
    ...

#3  Meera Pillai  —  48.63/100  [Weak Match]
    ...
```

The full ranked list (all 13 candidates, every scoring sub-component,
matched/missing skills, and reasoning) is written to
`output/ranked_candidates.csv` and `output/ranked_candidates.json`.

`ranked_candidates.json` excerpt:

```json
{
  "file": "resume_11_neha.txt",
  "name": "Neha Kapoor",
  "email": "neha.kapoor@email.com",
  "score": 55.2,
  "tier": "Possible Match",
  "semantic_similarity": 16.0,
  "skill_match_pct": 84.21,
  "experience_match_pct": 100.0,
  "matched_skills": ["aws", "azure", "docker", "..."],
  "missing_skills": ["data analysis", "data science", "gcp", "..."],
  "reasoning": "Matches 16 required skill(s): ... Experience: 7 yrs vs 3 yrs required (100% of target).",
  "rank": 1
}
```

---

## 6. Design tradeoffs (and what I'd improve)

### Scoring method: TF-IDF + weighted rule-based scoring, not an LLM call

**What I built:** a weighted blend of three explainable signals:

| Component               | Weight | What it measures                                       |
|--------------------------|:------:|----------------------------------------------------------|
| Semantic similarity      | 45%    | TF-IDF (1–2 gram) cosine similarity between JD and resume text |
| Skill match              | 35%    | Overlap between a keyword-taxonomy skill extraction of the JD and the resume |
| Experience match         | 20%    | Candidate's stated years vs. the JD's minimum, linear partial credit below the bar |

**Why this approach for a 24-hour build:**
- **Zero API key / fully reproducible.** A reviewer can clone the repo
  and get identical output with no signup, no rate limits, no network
  call, and no cost. This mattered more than raw accuracy for a
  timed take-home a reviewer needs to run themselves.
- **Explainable by construction.** Every score decomposes into named
  sub-scores and a plain-English reasoning string listing exactly
  which required skills matched or were missing — not a black-box
  number from a single LLM prompt.
- **Deterministic.** Same input always gives the same output/ranking,
  which makes the scoring method testable (see `tests/test_pipeline.py`).

**Known limitations of this approach:**
- **Keyword-based skill extraction misses synonyms/paraphrases** (e.g.
  a resume that says "built neural networks with PyTorch" but never
  writes the literal words "deep learning" won't get credit for that
  skill unless PyTorch itself is in the taxonomy — which it is here,
  but a smaller/adjacent taxonomy would miss it).
- **Negation handling is a simple word-window heuristic**, not full
  parsing. During testing I found the naive keyword matcher flagged
  *"No machine learning background"* as a positive skill match — I
  added a small negation-window check (`extractor.py::_is_negated`) to
  catch cases like this, but it won't catch every phrasing (e.g.
  negation more than 3 words before the skill, or "unfamiliar with").
- **TF-IDF similarity plateaus** on resumes that are topically related
  but use different vocabulary than the JD (e.g. a data engineer who
  never writes "machine learning" explicitly still scores low on
  semantic similarity even though they're plausibly adjacent).
- **Experience extraction** looks for explicit "`X years`" phrasing; a
  resume that only lists job start/end dates without ever saying
  "X years of experience" will be under-credited (defaults to 0).

### What I'd improve with more time

1. **Swap/augment TF-IDF with sentence embeddings** (e.g.
   `sentence-transformers`) for the semantic similarity component, so
   near-synonyms ("led," "managed," "owned") and paraphrased experience
   are captured, not just shared vocabulary.
2. **Add an optional LLM-reasoning pass** (Anthropic/OpenAI, gated
   behind an API key env var so it degrades gracefully to the current
   offline scorer if no key is set) that reads the top-N candidates and
   writes a richer, recruiter-style summary paragraph per candidate.
3. **Better experience extraction**: parse date ranges
   ("Jan 2020 – Present") and sum them, instead of relying only on
   explicit "X years" phrases.
4. **Section-aware parsing**: currently the whole resume is one blob of
   text; detecting "Skills" / "Experience" / "Education" sections would
   let skill matches from a "Skills" section be weighted more heavily
   than an incidental mention buried in a paragraph.
5. **Configurable/learned weights**: today `WEIGHTS` in `config.py` are
   fixed and hand-picked; with labeled hire/no-hire outcome data these
   could be calibrated (e.g. logistic regression over the three
   sub-scores) instead of guessed.
6. **PDF layout edge cases**: multi-column resumes or resumes with
   skills embedded in images (rather than text) will extract poorly —
   worth adding OCR fallback (e.g. `pytesseract`) for scanned PDFs.

---

## 7. How reviewers can reproduce a demo in under a minute

```bash
git clone <your-repo-url>
cd resume-screening-agent
pip install -r requirements.txt
python src/main.py --top 13
```

This uses the bundled sample JD and 13 sample resumes end-to-end — no
configuration, no API key, no extra setup required.
