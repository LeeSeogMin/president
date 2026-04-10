# Measuring Adaptive Governance Without Accumulation Bias

Multi-LLM Scoring Across Five Korean Administrations

한국 정부의 적응적 거버넌스 비교연구: 축적 편향 통제를 위한 다중 지표 설계

**Author**: Seogmin Lee (Hanshin University, School of Public Service, Big Data and Convergence)

## Overview

This repository contains the replication materials for a comparative study of adaptive governance across five completed Korean administrations (Roh Moo-hyun through Yoon Suk-yeol, 2003–2025). The study introduces a multi-indicator, flow-based scoring design that controls for **accumulation bias** — the systematic measurement confound arising when successor governments inherit institutional stock from predecessors.

Key features:
- **5 heterogeneous LLMs** (GPT-5.2, Claude 4.6, Grok-4-1, HCX-007, Gemini 3 Flash) as structured auxiliary scoring tools
- **3-round repeated measurement** with empirically tested blinding protocol
- **5 indicators**: T/I/D/E weighted score, AGLI, CRS, Lowi STRICT, WGI residual
- **Validation suite**: probe test, blinding comparison, zero-score rule test, model disagreement analysis

## Project Structure

```
president/
├── README.md
├── requirements.txt
├── .env.example                    # API key template
├── .gitattributes                  # Git LFS config
│
├── data/
│   ├── gov_factsheets.md           # Government background factsheets (input)
│   │
│   ├── scripts/                    # Python analysis pipeline
│   │   ├── ai_scoring_v2.py        # Core ACW/INST scoring (Panel 1+2)
│   │   ├── multi_round_scoring.py  # Repeated measurement (rounds 2-3)
│   │   ├── blind_coding.py         # T/I/D/E blind validation
│   │   ├── blind_validation_report.py  # Validation report generation
│   │   ├── crisis_scoring.py       # CRS crisis response scoring
│   │   ├── action_evaluation.py    # I/D action impact evaluation
│   │   ├── probe_test.py           # Blinding penetration test
│   │   ├── blinding_comparison.py  # Blinded vs unblinded comparison
│   │   └── zero_score_test.py      # No-zero-score rule test
│   │
│   ├── raw_downloads/              # External raw data
│   │   ├── wgi_full_dataset_2025.xlsx  # World Bank WGI (Git LFS, 9.9MB)
│   │   ├── wgi_korea_*.json        # WGI Korea indicators (7 files)
│   │   ├── wgi_oecd_38_GE_EST.json # OECD 38-country GE comparison
│   │   ├── oecd_dgi_full.csv       # OECD Digital Government Index
│   │   ├── un_egdi_korea_source.md # UN E-Government Development Index
│   │   └── crisis_timelines.md     # 15 crisis case timelines (input)
│   │
│   ├── verified/                   # Confirmed analysis results (reference)
│   │   ├── tide_attribution.md     # T/I/D/E coding table (researcher-coded)
│   │   ├── tide_weighted.md        # T/I/D/E weighted results
│   │   ├── agli_scoring_v2.md      # AGLI results
│   │   ├── composite_scoring.md    # Composite scores (Z-score, Borda)
│   │   ├── lowi_*.md               # Lowi classification and validation
│   │   ├── wgi_confidence.md       # WGI residual analysis
│   │   ├── adaptive_capacity_profile.md  # ACW 6-dimension profile
│   │   ├── laws_summary.md         # Legal text summary
│   │   └── laws/                   # 6 Korean legal texts (primary sources)
│   │
│   └── validation/                 # Methodology validation results
│       ├── OSF_README.md           # OSF replication package description
│       ├── probe_test_results.json # Blinding: 100% government identification
│       ├── probe_test_report.md    # Blinding analysis report
│       ├── blinding_comparison_results.json  # Blinded vs unblinded CRS
│       ├── blinding_comparison_report.md
│       ├── zero_score_test_results.json      # Zero-score rule effect
│       ├── zero_score_test_report.md
│       ├── disagreement_stability_results.json  # Model disagreement + stability
│       └── def_analysis_results.json  # Coding symmetry + CRS criteria
```

## Reproduction

### 1. Environment Setup

**Requirements**: Python 3.10+, Git LFS, internet connection (5 AI API calls)

```bash
# Clone repository
git clone https://github.com/LeeSeogMin/president.git
cd president

# Git LFS (for wgi_full_dataset_2025.xlsx, 9.9MB)
git lfs install
git lfs pull

# Python environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. API Key Setup

Copy `.env.example` to `.env` and add API keys for all 5 models:

```bash
cp .env.example .env
# Edit .env with your API keys
```

Required API keys:
- OpenAI (GPT-5.2)
- Anthropic (Claude Sonnet 4.6)
- xAI (Grok-4-1)
- Google (Gemini 3 Flash)
- NAVER Cloud (HyperCLOVA HCX-007)

### 3. Script Execution Order

**Prerequisites**: The following researcher-authored input files must exist before running scripts:
- `data/verified/tide_attribution.md` — T/I/D/E coding (input for scripts 3, 6)
- `data/gov_factsheets.md` — Government factsheets (input for script 1)
- `data/raw_downloads/crisis_timelines.md` — 15 crisis timelines (input for script 5)

All scripts are run from `data/scripts/`:

```bash
cd data/scripts
```

#### Core Analysis Pipeline

| Step | Script | Description | Output |
|:----:|--------|-------------|--------|
| 1 | `python ai_scoring_v2.py` | ACW/INST scoring (5 models, Panel 1+2) | `tables/scoring_v2_raw.json` |
| 2 | `python multi_round_scoring.py` | Repeated measurement (rounds 2-3) | `tables/scoring_v2_5round_avg.json` |
| 3 | `python blind_coding.py` | T/I/D/E borderline blind validation | `../raw_downloads/blind_coding_responses.json` |
| 4 | `python blind_validation_report.py` | Krippendorff alpha computation | `../verified/blind_validation_results.md` |
| 5 | `python crisis_scoring.py` | 15 crisis case response scoring | `../verified/crisis_response_score.md` |
| 6 | `python action_evaluation.py` | I/D action adaptive impact evaluation | `../raw_downloads/action_evaluation_raw.json` |

#### Validation Tests (can be run independently)

| Script | Description | Output |
|--------|-------------|--------|
| `python probe_test.py` | Blinding penetration test | `../validation/probe_test_results.json` |
| `python blinding_comparison.py` | Blinded vs unblinded CRS comparison | `../validation/blinding_comparison_results.json` |
| `python zero_score_test.py` | No-zero-score rule effect test | `../validation/zero_score_test_results.json` |

### 4. Key Execution Options

```bash
# ai_scoring_v2.py
python ai_scoring_v2.py --panel 1              # Panel 1 only
python ai_scoring_v2.py --models gpt gemini    # Specific models only
python ai_scoring_v2.py --reuse-panel1         # Reuse Panel 1 results

# multi_round_scoring.py
python multi_round_scoring.py --round 2        # Round 2 only
python multi_round_scoring.py --aggregate-only  # Aggregation only (no API calls)
```

## Data Sources

| Data | Source | File |
|------|--------|------|
| World Governance Indicators | World Bank | `wgi_full_dataset_2025.xlsx` |
| Digital Government Index | OECD | `oecd_dgi_full.csv` |
| E-Government Development Index | UN DESA | `un_egdi_korea_source.md` |
| Crisis case timelines | Researcher-collected | `crisis_timelines.md` |
| Legal texts | Korea Legislation Information Center | `verified/laws/` |

## Validation Results Summary

| Test | Result | Implication |
|------|--------|-------------|
| **Probe test** | 100% government identification (25/25) | Blinding ineffective due to structural event uniqueness |
| **Blinding comparison** | Mean CRS difference: 0.08 (4-point scale, 2%) | Scores driven by objective crisis characteristics, not blinding |
| **Zero-score test** | Top 3 ranking preserved; 23% zeros when permitted | No-zero rule suppressed central tendency without distorting rankings |
| **Model disagreement** | Park Geun-hye highest SD (0.540); HCX-007 primary source (36%) | Contested evaluations concentrated in impeached administrations |
| **Round stability** | SD range: 0.015 (Moon) – 0.117 (Park) | High scoring consistency across rounds |

## Limitations

- **LLM methodology**: LLMs serve as structured auxiliary scoring tools, not independent coders. Human coder benchmark is absent.
- **Blinding failure**: All 5 models identified all governments despite Level 2 blinding. However, blinded/unblinded score difference was negligible (mean 0.08).
- **AI non-determinism**: temperature=0.2 applied across all models, but responses may vary slightly upon re-execution. Three-round averaging and 5-model cross-validation ensure stability.
- **N=5**: Five administrations preclude statistical inference; analysis pursues systematic description through pattern matching.

## Note on the Lee Jae-myung Administration

The Lee Jae-myung administration, inaugurated following the Constitutional Court's 2025 impeachment decision, was excluded from analysis because its tenure of 0.8 years (as of March 2026) precludes equitable comparison with completed administrations. It will be examined in follow-up research upon term completion.

## Citation

> Lee, S. (2026). Measuring Adaptive Governance Without Accumulation Bias: Multi-LLM Scoring Across Five Korean Administrations. Submitted to *Policy Sciences*. Hanshin University.

## Acknowledgments

This work was supported by Hanshin University.

## License

Released for academic research purposes under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
