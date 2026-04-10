# Replication Package: Measuring Adaptive Governance Without Accumulation Bias

## Paper
Lee, S. (2026). Measuring Adaptive Governance Without Accumulation Bias: Multi-LLM Scoring Across Five Korean Administrations. Submitted to *Policy Sciences*.

## Contents

### Data
| File | Description |
|------|-------------|
| `data/scripts/tables/scoring_v2_raw.json` | Round 1 raw scores (5 models × 5 governments × ACW+INST) |
| `data/scripts/tables/rounds/round_2.json` | Round 2 raw scores |
| `data/scripts/tables/rounds/round_3.json` | Round 3 raw scores |
| `data/scripts/tables/scoring_v2_5round_avg.json` | 3-round averaged scores |
| `data/raw_downloads/crisis_timelines.md` | 15 crisis case timelines (input for CRS) |
| `data/raw_downloads/wgi_full_dataset_2025.xlsx` | World Bank WGI dataset (Git LFS) |
| `data/raw_downloads/wgi_korea_*.json` | WGI Korea indicators (7 files) |
| `data/raw_downloads/oecd_dgi_full.csv` | OECD Digital Government Index |
| `data/verified/tide_attribution.md` | T/I/D/E coding table (researcher-coded) |
| `data/verified/laws/` | 6 Korean legal texts (primary sources) |
| `data/gov_factsheets.md` | Government background factsheets |

### Scripts
| File | Description | API Required |
|------|-------------|:------------:|
| `data/scripts/ai_scoring_v2.py` | Core ACW/INST scoring (Panel 1+2) | Yes (5 keys) |
| `data/scripts/multi_round_scoring.py` | Repeated measurement (rounds 2-3) | Yes |
| `data/scripts/blind_coding.py` | T/I/D/E blind validation | Yes |
| `data/scripts/blind_validation_report.py` | Validation report generation | No |
| `data/scripts/crisis_scoring.py` | CRS crisis response scoring | Yes |
| `data/scripts/action_evaluation.py` | I/D action impact evaluation | Yes |
| `data/scripts/probe_test.py` | Blinding penetration test | Yes |
| `data/scripts/blinding_comparison.py` | Blinded vs unblinded comparison | Yes |
| `data/scripts/zero_score_test.py` | No-zero-score rule test | Yes |

### Validation Results
| File | Description |
|------|-------------|
| `paper_a/probe_test_results.json` | Probe test: 100% government identification |
| `paper_a/probe_test_report.md` | Probe test analysis report |
| `paper_a/blinding_comparison_results.json` | Blinded vs unblinded CRS scores |
| `paper_a/blinding_comparison_report.md` | Blinding comparison analysis |
| `paper_a/zero_score_test_results.json` | Zero-score rule effect test |
| `paper_a/zero_score_test_report.md` | Zero-score test analysis |
| `paper_a/disagreement_stability_results.json` | Model disagreement + round stability |
| `paper_a/def_analysis_results.json` | Coding symmetry + CRS criteria + heterogeneity |

## Environment
- Python 3.10+
- Dependencies: `pip install -r requirements.txt` (numpy, requests, python-dotenv)
- API keys required: OpenAI, Anthropic, xAI, Google, NAVER Cloud (see `.env.example`)
- All scripts use `temperature=0.2`

## Reproduction
1. Clone repository
2. `cp .env.example .env` and add API keys
3. Run scripts in order: `ai_scoring_v2.py` → `multi_round_scoring.py` → remaining scripts
4. Validation scripts can be run independently

## Note
Due to LLM non-determinism, exact scores may vary slightly upon re-execution. The replication package preserves the original scoring data used in the paper.
