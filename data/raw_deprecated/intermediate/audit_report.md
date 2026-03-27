# Research Integrity Audit Report

> Audit date: 2026-03-26
> Auditor: Independent AI audit (Claude Opus 4.6)
> Scope: All files in `/data/verified/`, cross-referenced against `data_collection_plan.md`
> Principle: Honest reporting. Problems are flagged without softening.

---

## Executive Summary

The project underwent a major data overhaul after discovering that original data was AI-fabricated. The rebuilt dataset is substantially more rigorous than the original, with verified sources for most data points. However, **several gaps, inconsistencies, and incomplete items remain**. This report documents them all.

**Overall assessment**: The data infrastructure is solid but incomplete. The methodology is well-designed but partially executed. Honest self-reporting of limitations (e.g., ACW draft status, data gaps) is a positive sign of research integrity. However, some cross-file inconsistencies need correction before publication.

---

## 1. Data Completeness Audit

### 1.1 Planned vs. Actual Data Collection

| Planned Item (data_collection_plan.md) | Planned Output | Actual Output | Status |
|----------------------------------------|----------------|---------------|--------|
| 1-1. WGI 시계열 (World Bank API) | `wgi_korea.csv` | `wgi_korea.md` | **FORMAT MISMATCH** -- collected as .md, not .csv as planned |
| 1-2. OECD DGI (SDMX API) | `oecd_dgi_korea.csv` | `oecd_dgi_korea.md` | **FORMAT MISMATCH** -- .md not .csv |
| 1-3. UN EGDI (Data360 API) | `un_egdi_korea.csv` | `un_egdi_korea.md` | **FORMAT MISMATCH** -- .md not .csv |
| 1-4. 법률 원문 (6개) | `laws/` (JSON) | `laws/` (6 .md files) | **FORMAT MISMATCH** -- collected as .md, not JSON |
| 1-5. Policy Lag 검증 | `policy_lag_verified.md` | `policy_lag_verified.md` | **COMPLETE** |
| 2-1. 학술 인용 3건 교체 | (paper corrections) | **NOT FOUND** in verified/ | **MISSING** |
| 2-2. 국정과제 수 정정 | (paper corrections) | Partially in lowi_classification.md | **PARTIAL** |
| 2-3. 기존 파일 처리 | raw_deprecated/ | Confirmed in plan as completed | OK |
| 3-1. Lowi 재분류 (595개) | `lowi_classification.csv` | `lowi_classification.md` | **FORMAT MISMATCH** -- .md not .csv; content COMPLETE |
| 3-2. ACW 재코딩 | `acw_scoring_verified.md` | `acw_scoring_draft.md` | **INCOMPLETE** -- still DRAFT, almost entirely "INSUFFICIENT DATA" |
| 3-3. INST 재코딩 | `inst_scoring_verified.md` | `inst_scoring_verified.md` | **COMPLETE** |

### 1.2 Additional Files Created (Not in Original Plan)

These files were created beyond the original plan, representing methodological evolution:

| File | Purpose | Status |
|------|---------|--------|
| `action_inventory.md` | Layer 1 of 3-layer methodology | Complete |
| `tide_attribution.md` | Layer 2: T/I/D/E coding | Complete |
| `blind_validation_results.md` | Layer 3: AI blind validation | Complete |
| `action_evaluation_results.md` | AI action evaluation (Step 6) | Complete |
| `bias_removal_methodology.md` | Methodology design document | Complete |
| `methodology_note_accumulation_bias.md` | Accumulation bias theory | Complete |
| `wgi_oecd_comparison.md` | OECD 38-country WGI comparison | Complete |
| `roh_detailed_tasks.md` | Roh Moo-hyun detailed subtasks | Complete |
| `assembly_bills.md` | National Assembly API data | Complete |
| `decisions_log.md` | Decision log | Complete but minimal |

### 1.3 Completeness Verdict

**Critical gaps:**
1. **ACW scoring is essentially empty.** The `acw_scoring_draft.md` file marks nearly every cell as "INSUFFICIENT DATA" with LOW confidence. This is a core analytical component that remains unbuilt. The plan called for `acw_scoring_verified.md` (final), but only a draft shell exists.
2. **Academic citation replacements (2-1) have no deliverable** in the verified/ directory. No record of which citations replaced the 3 fabricated ones.
3. **All output files are .md instead of .csv** as originally planned. This is a minor format issue but means no machine-readable data files exist.

**Positive notes:**
- The 3-layer methodology (Action Inventory, T/I/D/E, Blind Validation) was not in the original plan but represents a significant methodological upgrade.
- Raw API responses ARE saved in `data/raw_downloads/` with 14 files including JSON, CSV, XLSX, and PDF sources.

---

## 2. Data Accuracy (Cross-File Consistency)

### 2.1 WGI Numbers: `action_inventory.md` vs `wgi_korea.md`

| Government | Metric | action_inventory.md | wgi_korea.md | Match? |
|------------|--------|--------------------:|-------------:|--------|
| 노무현 | GE.EST start (2003) | 0.790 | 0.790 | YES |
| 노무현 | GE.EST end (2007) | 1.202 | 1.202 | YES |
| 노무현 | Avg EST | 0.943 | 0.943 | YES |
| 이명박 | GE.EST start (2008) | 0.994 | 0.994 | YES |
| 이명박 | GE.EST end (2012) | 1.075 | 1.075 | YES |
| 이명박 | Avg EST | 1.080 | 1.080 | YES |
| 박근혜 | GE.EST start (2013) | 1.003 | 1.003 | YES |
| 박근혜 | GE.EST end (2016) | 1.021 | 1.021 | YES |
| 박근혜 | Avg EST | 1.009 | 1.009 | YES |
| 문재인 | GE.EST start (2017) | 1.029 | 1.029 | YES |
| 문재인 | GE.EST end (2021) | 1.366 | 1.366 | YES |
| 문재인 | Avg EST | 1.247 | 1.247 | YES |
| 윤석열 | GE.EST start (2022) | 1.349 | 1.349 | YES |
| 윤석열 | GE.EST end (2023) | 1.405 | 1.405 | YES |
| 윤석열 | Avg EST | 1.377 | 1.377 | YES |

**WGI data is fully consistent across files.**

### 2.2 INST Scores: `action_inventory.md` vs `inst_scoring_verified.md`

| Government | D1 | D2 | D3 | D4 | Total | Match? |
|------------|:--:|:--:|:--:|:--:|:-----:|--------|
| 노무현 | 2/2 | 0/0 | 1/1 | 1/1 | 4/4 | YES |
| 이명박 | 2/2 | 0/0 | 1/1 | 1/1 | 4/4 | YES |
| 박근혜 | 2/2 | 0/0 | 1/1 | 1/1 | 4/4 | YES |
| 문재인 | 2/2 | 2/2 | 1/1 | 1/1 | 6/6 | YES |
| 윤석열 | 2/2 | 2/2 | 1/1 | 1/1 | 6/6 | YES |
| 이재명 | 2/2 | 2/2 | 1/1 | 2/2 | 7/7 | YES |

**INST scores are fully consistent across files.**

### 2.3 Policy Lag Dates: `action_inventory.md` vs `policy_lag_verified.md`

| Case | Metric | action_inventory.md | policy_lag_verified.md | Match? |
|------|--------|--------------------:|----------------------:|--------|
| 2008 금융위기 | First response | 2008.09.16 / 1일 | 2008.09.16 / 1일 | YES |
| 2008 금융위기 | Comprehensive | 2008.10.19 / 34일 | 2008.10.19 / 34일 | YES |
| 2015 MERS | President response | 2015.06.03 / 14일 | 2015.06.03 / 14일 | YES |
| 2015 MERS | Supplementary budget | 2015.07.24 / 65일 | 2015.07.24 / 65일 | YES |
| 2020 COVID-19 | First response | 2020.01.20 / 0일 | 2020.01.20 / 0일 | YES |
| 2020 COVID-19 | 1st supplementary | 2020.03.17 / 57일 | 2020.03.17 / 57일 | YES |
| 이태원 참사 | Mourning | 2022.10.30 / 1일 | 2022.10.30 / 1일 | YES |
| 이태원 참사 | Special law | 2024.05.21 / 571일 | 2024.05.21 / 571일 | YES |

**Policy Lag dates are fully consistent across files.**

### 2.4 Lowi Percentages: `action_inventory.md` vs `lowi_classification.md`

| Government | Total | Dist. | Reg. | Redist. | Const. | Adaptive | Match? |
|------------|:-----:|:-----:|:----:|:-------:|:------:|:--------:|--------|
| 노무현 | 12/12 | 4(33.3%)/4(33.3%) | 2(16.7%)/2(16.7%) | 1(8.3%)/1(8.3%) | 5(41.7%)/5(41.7%) | 0.0%/0.0% | YES |
| 이명박 | 100/100 | 33(33.0%)/33(33.0%) | 18(18.0%)/18(18.0%) | 22(22.0%)/22(22.0%) | 27(27.0%)/27(27.0%) | 0.0%/0.0% | YES |
| 박근혜 | 140/140 | 41(29.3%)/-- | 36(25.7%)/-- | 30(21.4%)/-- | 33(23.6%)/-- | 3.6%/-- | YES (spot-checked) |
| 문재인 | 100/100 | 24(24.0%)/-- | 18(18.0%)/-- | 24(24.0%)/-- | 34(34.0%)/-- | 2.0%/-- | YES (spot-checked) |
| 윤석열 | 120/120 | 43(35.8%)/-- | 22(18.3%)/-- | 23(19.2%)/-- | 32(26.7%)/-- | 10.0%/-- | YES (spot-checked) |
| 이재명 | 123/123 | 37(30.1%)/-- | 22(17.9%)/-- | 22(17.9%)/-- | 42(34.1%)/-- | 10.6%/-- | YES (spot-checked) |

**Lowi data is consistent across files.**

### 2.5 Identified Inconsistency: AI Basic Act Law Numbers

| File | AI Basic Act Law Number | Promulgation Date |
|------|------------------------|-------------------|
| `policy_lag_verified.md` | **제20676호** | **2025.01.21** |
| `laws/01_ai_basic_act.md` | 제21311호 (latest revision); 원제정: **제20676호** | 원제정: 2025.01.22 |
| `laws_summary.md` | **제21311호** | 2026.1.20 |
| `action_inventory.md` (윤석열) | **제20676호** | 2025.01.21 |
| `action_inventory.md` (이재명) | **제21311호** | 2026.01.20 |

**ISSUE FOUND**: The original promulgation date is inconsistent:
- `policy_lag_verified.md` says 2025.01.**21** (공포일)
- `laws/01_ai_basic_act.md` says 원제정: 2025.1.**22**
- These differ by 1 day. One of these must be wrong. The `policy_lag_verified.md` cites the law.go.kr URL with "20250121" in the path, which supports 01.21 as the correct date. The .22 in the law file may be a typo confusing the promulgation date with the enforcement date (시행일: 2026.01.22).

**ISSUE FOUND**: `laws_summary.md` row 4 (이태원참사특별법) shows 법률번호 **제21065호**, 공포일 2025.10.1 -- this is clearly wrong. 제21065호 is the 정부업무평가기본법 number. The 이태원특별법 has a different number. This appears to be a **copy-paste error** in `laws_summary.md`.

---

## 3. Methodology Integrity (T/I/D/E Coding)

### 3.1 Coding Consistency

The T/I/D/E coding in `tide_attribution.md` follows clear, documented rules from `bias_removal_methodology.md`. Each action has:
- Explicit T/I/D/E code
- Confidence level (HIGH/MEDIUM/LOW)
- Written justification
- Borderline flag (Y/N)

**Positive findings:**
- The coding distinguishes between law creation (I) and law inheritance (T) consistently across all 6 governments.
- WGI detrending uses a consistent linear trend of +0.026/year (R^2=0.73) for all governments.
- External events (crises) are properly separated: the event itself coded E, the response coded I or D.
- 30 borderline cases are explicitly flagged for AI validation.

**Potential concerns:**
1. **Researcher may over-code "I" for current government actions.** Lee Jae-myung's AI Basic Act implementation (이재명-A1) is coded I, but the law was passed by the 22nd National Assembly and signed by Yoon. Only the operational implementation is attributable to Lee. The coding acknowledges this but still assigns I. This is a judgment call, not an error.
2. **Yoon's favorable actions may be under-credited.** DGI 2023 (0.935, 1st place) is coded T+I, but DGI 2025 (0.95, still 1st) is coded T only. The rationale (small increment, OECD gap narrowing) is defensible but could be debated.

### 3.2 윤석열 계엄 항목 (G1, G2) Integration

**Status: Properly integrated.**

- G1 (2024.12.03 비상계엄 선포) and G2 (탄핵 소추 및 헌법재판소 심판) are both:
  - Included in `tide_attribution.md` with I- coding and HIGH confidence
  - Accompanied by a substantial qualitative narrative explaining why quantitative T/I/D/E coding is insufficient
  - Noted in `action_evaluation_results.md` as "N/A" for AI evaluation (excluded from quantitative scoring)
  - The rationale for exclusion from AI evaluation is sound: the event transcends the analytical framework's assumptions

**Assessment**: The handling of the martial law episode is methodologically honest. It would have been easier to simply assign a negative score, but the researchers correctly note that the framework assumes functioning democratic institutions, and an attempt to destroy those institutions exceeds the framework's scope. The qualitative treatment is appropriate.

---

## 4. AI Evaluation Integrity

### 4.1 Blind Validation Results

**5 models used**: GPT-5.2, Claude-Sonnet-4.6, Grok-4-1, Gemini-3-Flash, HCX-007.

**Identification test**: All 5 models scored 0/1 (0%) on identifying which blinded government label corresponded to which real government. Blinding was successful.

**Krippendorff's Alpha**:
- Inter-model: alpha = 0.6734
- Including researcher: alpha = 0.6460

These values indicate "tentative" agreement (0.667 threshold for tentative, 0.80 for reliable). This is honestly reported and not inflated.

**Concerns:**
1. **HCX-007 only produced 5 responses out of 46** (noted as "토큰 한계로 부분 응답"). Its 20% agreement rate is anomalous. Including it in aggregate statistics without heavy caveats could be misleading, but it IS flagged.
2. **GPT-5.2 parsing failure** in Task 2 (action evaluation). Only 3 models (Claude, Grok, Gemini) contributed to the action evaluation scores. This is properly noted ("GPT-5.2: 파싱 실패").
3. **All 54/54 items flagged as "시대 민감" (time-sensitive)** in Task 3. A 100% rate suggests the test may lack discriminating power -- if everything is time-sensitive, the test doesn't help distinguish actions.

### 4.2 Action Evaluation Results

**Potential red flag: Suspiciously unanimous voting patterns.**

Many items show 9:0:0 or 0:0:9 voting distributions (3 models x 3 rounds = 9 votes). For example:
- 노무현-A1: +1:9 0:0 -1:0
- 윤석열-D1: +1:0 0:0 -1:9
- 문재인 entire block: nearly all 9:0:0

Only a few items show split votes (e.g., 노무현-E1: +1:0 0:5 -1:4; 박근혜-E1: +1:6 0:3 -1:0).

**Assessment**: The unanimity is not necessarily fabricated. The evaluation criteria (+1/0/-1) are relatively coarse, and many actions have obvious valence (creating a new law = obviously +1, crisis response failure = obviously -1). The split votes on genuinely ambiguous items (e.g., "adaptive tool ratio 0% but early period") are actually a sign of honest reporting. If results were fabricated, one would expect either perfect unanimity OR artificially varied distributions.

### 4.3 Fabrication Risk Assessment

**Low fabrication risk.** Evidence:
- Raw JSON files exist in `data/raw_downloads/` (`action_evaluation_raw.json`, `blind_coding_responses.json`)
- The file sizes (185KB, 158KB) are consistent with actual multi-model API responses
- HCX-007's partial failure is a realistic artifact that a fabricator would be unlikely to include
- GPT-5.2's parsing failure is similarly realistic
- Disagreement patterns match expected AI behavior (models occasionally disagree on borderline cases)

**Cannot fully verify** without inspecting the raw JSON contents, but the metadata is consistent with genuine API calls.

---

## 5. Missing Pieces

### 5.1 Data Planned but NOT Collected

| Item | Plan Reference | Status | Impact |
|------|---------------|--------|--------|
| ACW 22기준 재코딩 | Phase 3, 3-2 | **NOT DONE** -- only a shell draft exists | **CRITICAL**: ACW is one of the two core scoring frameworks. Without it, only INST scores remain for institutional comparison. |
| 학술 인용 3건 교체 | Phase 2, 2-1 | **NO DELIVERABLE** found | **MODERATE**: Affects paper credibility if fabricated citations remain |
| CSV format files | All Phase 1 outputs | All delivered as .md | **LOW**: Content is present; format is different |

### 5.2 Decisions Made but NOT Implemented

Checking `decisions_log.md` (5 decisions):

| # | Decision | Implementation Status |
|---|---------|---------------------|
| 1 | WGI 기준: 최신 API (소급 개정), footnote required | **PARTIALLY IMPLEMENTED** -- WGI data uses latest API values. wgi_korea.md notes "Access Date: 2026-03-26". However, the required footnote "accessed 2026-03, retroactively revised" is not visible in the data files (it would go in the paper). |
| 2 | OECD 평균 WGI 수집 (38개국 DiD 대조군) | **IMPLEMENTED** -- `wgi_oecd_comparison.md` contains 37-country OECD averages (excl. Korea). Raw data in `raw_downloads/wgi_oecd_38_GE_EST.json`. |
| 3 | 노무현 세부과제 수집 (기한 1주) | **IMPLEMENTED** -- `roh_detailed_tasks.md` contains 12 major tasks with subtasks from the 2003 인수위 document. Primary source PDF confirmed. |
| 4 | AI 재평가: 3 rounds x 3 tasks x 5 models | **PARTIALLY IMPLEMENTED** -- Blind validation ran 3 rounds on 46 items. Action evaluation ran Task 2 (3 rounds) and Task 3 (1 round). However, GPT-5.2 failed parsing for Task 2 and HCX-007 had token limits. Effectively 3 models for Task 2. |
| 5 | 블라인드 실패 대응: 사전 의사결정 트리 | **IMPLEMENTED** -- Blinding succeeded (0% identification across all models), so the fallback decision tree was not needed. |

### 5.3 Unresolved Issues from Original Plan (Section 7)

| # | Issue | Resolution |
|---|-------|-----------|
| 1 | WGI 기준 시점 | Resolved (Decision #1) |
| 2 | 노무현 국정과제 단위 | Resolved -- both 12 macro tasks and detailed subtasks collected |
| 3 | ACW 코딩 방식 | **UNRESOLVED** -- ACW not coded at all. The entire ACW scoring framework remains a draft shell. |
| 4 | 이재명 정부 국제지표 부재 | Handled -- marked as "데이터 없음" throughout action_inventory.md |

---

## 6. Documentation Completeness

### 6.1 Source Traceability

| Data File | Sources Cited? | URLs/References? |
|-----------|:--------------:|:----------------:|
| wgi_korea.md | YES | YES -- World Bank API URLs |
| oecd_dgi_korea.md | YES | YES -- 7 primary sources with URLs |
| un_egdi_korea.md | YES | YES -- UN EGOVKB URL + 2024 report |
| policy_lag_verified.md | YES | YES -- news article URLs for each date |
| inst_scoring_verified.md | YES | YES -- law.go.kr references |
| lowi_classification.md | YES | YES -- classification criteria cited |
| laws/ (6 files) | YES | YES -- law.go.kr URLs |
| assembly_bills.md | YES | YES -- 열린국회정보 API |
| action_inventory.md | YES | YES -- cross-references to other verified files |
| tide_attribution.md | YES | YES -- references action_inventory.md and methodology |
| blind_validation_results.md | YES | Partial -- references script `blind_coding.py` |
| action_evaluation_results.md | YES | Partial -- references `raw_downloads/action_evaluation_raw.json` |
| acw_scoring_draft.md | YES | N/A -- all cells marked INSUFFICIENT DATA |

### 6.2 Raw API Responses

`data/raw_downloads/` contains 14 files:

| File | Size | Description |
|------|------|-------------|
| wgi_korea_GE_EST.json | 5.7KB | WGI Government Effectiveness estimates |
| wgi_korea_GE_PERCENTILE.json | 6.0KB | WGI percentile ranks |
| wgi_oecd_38_GE_EST.json | 213KB | OECD 38-country WGI data |
| wgi_full_dataset_2025.xlsx | 10.4MB | Full WGI dataset |
| wgi_korea_*.json (4 others) | ~5-6KB each | CC, RL, RQ, VA estimates |
| oecd_dgi_full.csv | 154KB | OECD DGI full dataset |
| roh_policy_tasks_2003.pdf | 20KB | Roh administration policy document |
| blind_coding_responses.json | 158KB | Raw AI blind validation responses |
| action_evaluation_raw.json | 186KB | Raw AI action evaluation responses |
| README.md | 2.7KB | Directory documentation |

**Assessment**: Raw downloads are well-preserved. The presence of both JSON API responses and the processed .md files provides an audit trail. However:
- **No raw UN EGDI API response** is saved (the UN data in `un_egdi_korea.md` cites the UN website but no raw download is preserved)
- **No raw law.go.kr scrape outputs** are saved (the laws/ directory contains processed summaries, not raw HTML/JSON)
- **No raw lowi classification working files** (the 595-task classification was presumably done manually, but no intermediate workfiles exist)

### 6.3 Expert Reports

The methodology notes reference "전문가 패널 5인" and "전문가 3인 조사 결과" but **no expert reports are saved as separate documents** in the verified/ directory. The expert input appears to have been integrated directly into methodology documents rather than preserved as standalone reports.

---

## 7. Summary of All Findings

### CRITICAL Issues (Must Fix Before Publication)

| # | Issue | Location | Description |
|---|-------|----------|-------------|
| C1 | ACW framework not completed | acw_scoring_draft.md | Nearly every cell is "INSUFFICIENT DATA". This was a core planned component. Either complete the ACW scoring or explicitly remove it from the research design and justify the omission. |
| C2 | laws_summary.md copy-paste error | laws_summary.md row 4 | 이태원특별법 has wrong 법률번호 (제21065호) and wrong dates (2025.10.1). These belong to 정부업무평가기본법. |

### MODERATE Issues (Should Fix)

| # | Issue | Location | Description |
|---|-------|----------|-------------|
| M1 | AI Basic Act promulgation date discrepancy | policy_lag_verified.md vs laws/01_ai_basic_act.md | One says 2025.01.21, the other says 2025.01.22. Verify against law.go.kr. |
| M2 | Academic citation replacements missing | Not found | Plan called for replacing 3 fabricated citations (손호중 2007, 조성한 2011, 정재호 2015). No record of what they were replaced with. |
| M3 | Task 3 lacks discriminating power | action_evaluation_results.md | 54/54 (100%) items flagged as time-sensitive. If everything is positive, the test adds no information. |
| M4 | Raw UN EGDI data not preserved | raw_downloads/ | No raw API response or download for UN EGDI data. |

### MINOR Issues (Informational)

| # | Issue | Location | Description |
|---|-------|----------|-------------|
| m1 | File format mismatch with plan | All Phase 1 outputs | Plan specified .csv; all delivered as .md. Content is equivalent. |
| m2 | No intermediate Lowi coding workfiles | verified/ | 595-task classification has no audit trail of coding decisions |
| m3 | Expert reports not separately preserved | verified/ | Expert panel input integrated into documents, not saved standalone |
| m4 | DGI 2025 API vs PDF discrepancy | oecd_dgi_korea.md | API shows composite 0.93, PDF report says 0.95. File notes the difference (rounding in weighted sum) but this should be explicitly addressed in the paper. |
| m5 | HCX-007 limited participation | blind_validation_results.md | Only 5/46 items answered due to token limits. Including it as a "5th model" in methodology claims may overstate the validation breadth. |

### Positive Findings (Things Done Right)

1. **Honest self-reporting**: The ACW file is labeled "DRAFT" with "INSUFFICIENT DATA". The researchers did not fabricate scores to fill gaps.
2. **Source traceability**: Nearly every data point has a URL or document reference.
3. **Error correction transparency**: All 5 original errors (from AI-fabricated data) are documented in `policy_lag_verified.md` with before/after values.
4. **Methodological evolution**: The 3-layer hybrid methodology (Action Inventory / T/I/D/E / Blind AI Validation) is a significant improvement over the original single-layer approach.
5. **Blind validation integrity**: The blinding protocol worked (0% identification), and disagreements are honestly reported rather than hidden.
6. **Raw data preservation**: 14 files in raw_downloads/ provide an audit trail for the key data sources.
7. **Martial law handling**: The 윤석열 G1/G2 events are treated with appropriate methodological honesty -- neither buried nor weaponized, but properly qualified as exceeding the framework's scope.

---

## 8. Recommendations

1. **Complete or formally abandon the ACW framework.** The current state (empty draft) is a liability. Either invest the time to score it properly with primary sources, or restructure the paper to rely solely on the INST + T/I/D/E framework.
2. **Fix the laws_summary.md copy-paste error** (이태원특별법 row has 정부업무평가기본법 data).
3. **Verify the AI Basic Act promulgation date** (01.21 vs 01.22) against the official law.go.kr page and standardize across all files.
4. **Document the citation replacements** even if the actual paper has been updated -- create a record of what replaced the 3 fabricated citations.
5. **Save raw UN EGDI data** to raw_downloads/ for complete audit trail.
6. **Address DGI 2025 API/PDF score discrepancy** explicitly in any published paper.
7. **Consider whether HCX-007 should be reported as a full 5th model** given its 5/46 completion rate.

---

*This audit was conducted by reading all files in the verified/ directory, cross-referencing data points across files, checking against the data_collection_plan.md, and evaluating methodology documents. No data was modified during the audit.*

*Auditor: Claude Opus 4.6 (1M context)*
*Audit date: 2026-03-26*
