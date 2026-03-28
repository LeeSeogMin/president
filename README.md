# 한국 역대 정부 적응적 거버넌스 역량 비교 연구

> **저자**: 이석민, 한신대학교 공공인재빅데이터융합학부
> **분석 기간**: 2003-2026 (노무현~이재명, 6개 정부)
> **방법론**: 다중 AI 스코어링 (5모델 × 3라운드) + 개념적 분석

---

---

## 데이터 흐름 (Data Lineage)

제3자가 재현할 때 **어떤 원시 데이터가 어떤 결과 파일을 생성하는지** 추적할 수 있어야 합니다.

### 지표별 데이터 경로

```
[지표 1] T/I/D/E Hall 3차수 가중합
  원본: 연구자 1인 코딩 (paper/paper_a_draft.md 부록 A)
  검증: data/scripts/blind_coding.py
       → input:  data/verified/tide_weighted.md (코딩표)
       → output: data/raw_downloads/blind_coding_responses.json (AI 원시 응답)
  결과: data/verified/tide_weighted.md

[지표 2] AGLI (적응적 거버넌스 법제도 지표)
  원본: data/verified/laws/ (법률 원문 6건)
  스코어링: data/scripts/ai_scoring_v2.py --panel 1 (INST 분석)
       → output: data/scripts/tables/scoring_v2_raw.json (5모델 원시 점수)
  결과: data/verified/agli_scoring_v2.md

[지표 3] Lowi STRICT 적응적 도구 비율
  원본: data/verified/lowi_classification.md (595개 국정과제 분류)
  검증: data/verified/lowi_validation.md (kappa=0.898)
  결과: data/verified/lowi_strict_review.md

[지표 4] CRS (위기 대응 적절성 점수)
  원본: data/raw_downloads/crisis_timelines.md (20건 위기 타임라인)
  스코어링: data/scripts/crisis_scoring.py
       → output: data/raw_deprecated/crisis_scoring_results.json (5모델 원시 채점)
  결과: data/verified/crisis_response_score.md

[지표 5] WGI 추세제거 잔차 (탐색적)
  원본: data/raw_downloads/wgi_full_dataset_2025.xlsx (World Bank API)
       data/raw_downloads/wgi_korea_GE_EST.json
  결과: data/verified/wgi_confidence.md

[ACW 프로파일] 적응역량 프로파일 (파생 요약)
  원본: data/scripts/ai_scoring_v2.py --panel 1 (ACW 분석)
       → output: data/scripts/tables/scoring_v2_raw.json (5모델 원시 점수)
       → output: data/scripts/tables/scoring_v2_5round_avg.json (3라운드 평균)
  결과: data/verified/adaptive_capacity_profile.md

[Panel 2] 이재명 지방정부 (성남시장·경기도지사)
  원본: data/verified/panel2_ljm_local_gov.md (지방정부 정책 데이터)
       data/verified/tide_governor_ljm.md (T/I/D/E 경기도지사)
  스코어링: data/scripts/ai_scoring_v2.py --panel 2
       → output: data/scripts/tables/scoring_v2_raw.json (panel2_acw, panel2_inst)
  분석: data/verified/ljm_leadership_analysis.md
  팩트시트: data/gov_factsheets.md (6개 정부 동등 배경)

[종합] Composite Scoring
  입력: 위 5개 지표 결과
  결과: data/verified/composite_scoring.md (Z-score, Min-Max, Borda)
```

### 스크립트 → 출력 매핑

| 스크립트 | 주요 출력 | 위치 |
|----------|----------|------|
| ai_scoring_v2.py | 5모델 원시 점수 JSON | `data/scripts/tables/scoring_v2_raw.json` |
| ai_scoring_v2.py | 통합 보고서 | `data/scripts/tables/scoring_v2_report.md` |
| multi_round_scoring.py | 라운드별 JSON | `data/scripts/tables/rounds/round_N.json` |
| multi_round_scoring.py | 3라운드 평균 JSON | `data/scripts/tables/scoring_v2_5round_avg.json` |
| blind_coding.py | AI 블라인드 응답 | `data/raw_downloads/blind_coding_responses.json` |
| crisis_scoring.py | CRS 원시 채점 JSON | `data/raw_deprecated/crisis_scoring_results.json` |
| crisis_scoring.py | CRS 결과 | `data/verified/crisis_response_score.md` |
| action_evaluation.py | 행위 평가 JSON | `data/raw_downloads/action_evaluation_raw.json` |

---

## 재현 방법 (Reproducibility)

### 1. 환경 설정

```bash
git clone https://github.com/LeeSeogMin/president.git
cd president
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Python 버전**: 3.10 이상 권장 (개발 환경: 3.14)

### 2. API 키 설정

```bash
cp .env.example .env
# .env 파일을 열어 실제 API 키 입력
```

5개 모델의 API 키가 모두 필요합니다:

| 모델 | 환경 변수 | 발급처 |
|------|----------|--------|
| GPT-5.2 | `OPENAI_API_KEY` | [OpenAI](https://platform.openai.com) |
| Claude Sonnet 4.6 | `ANTHROPIC_API_KEY` | [Anthropic](https://console.anthropic.com) |
| Grok-4-1 | `XAI_API_KEY` | [xAI](https://console.x.ai) |
| Gemini 3 Flash | `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com) |
| HyperCLOVA HCX-007 | `CLOVA_STUDIO_API_KEY` + `NCP_ACCESS_KEY_ID` + `NCP_SECRET_KEY` | [NAVER Cloud](https://www.ncloud.com/product/aiService/clovaStudio) |

### 3. 스크립트 실행 (순서 준수)

#### Step 1: 핵심 AI 스코어링 (ACW/제도/Lowi)

```bash
python data/scripts/ai_scoring_v2.py                    # 전체 (Panel 1 + Panel 2)
python data/scripts/ai_scoring_v2.py --panel 1           # 중앙정부만
python data/scripts/ai_scoring_v2.py --panel 2           # 지방정부만
```

6개 정부에 동등한 배경 팩트시트(`data/gov_factsheets.md`)를 주입하여 정보 대칭을 확보합니다.
출력: `data/scripts/tables/scoring_v2_raw.json`, `data/scripts/tables/scoring_v2_report.md`

코더 간 신뢰도: Fleiss' kappa(명목) + **Krippendorff's alpha(ordinal)** 병행 산출.

#### Step 2: 반복 측정 (3라운드)

```bash
python data/scripts/multi_round_scoring.py --round 2 --round 3
python data/scripts/multi_round_scoring.py --aggregate-only   # 집계만
```

Step 1의 1회차 + 추가 2회 = 총 3라운드 평균 산출.
출력: `data/scripts/tables/rounds/round_N.json`, `data/scripts/tables/scoring_v2_5round_avg.json`

#### Step 3: T/I/D/E 블라인드 검증

```bash
python data/scripts/blind_coding.py
```

`data/verified/tide_weighted.md`의 경계 사례를 Level 2 블라인드 처리 후 5모델 × 3라운드로 검증.
출력: `data/raw_downloads/blind_coding_responses.json`

#### Step 4: 위기 대응 채점 (CRS)

```bash
python data/scripts/crisis_scoring.py
```

`data/raw_downloads/crisis_timelines.md`의 위기 사례를 **Level 2 블라인드**(대통령명·정당명·고유사건명·연도 치환) 처리 후 5모델이 3차원(인지·적절성·집행) × 0-4로 채점.
출력: `data/raw_deprecated/crisis_scoring_results.json`, `data/verified/crisis_response_score.md`

#### Step 5: 행위 평가

```bash
python data/scripts/action_evaluation.py
```

I/D 유형 행위의 적응적 거버넌스 영향(+1/0/-1)과 시간민감도(2003 vs 2023) 평가.
출력: `data/raw_downloads/action_evaluation_raw.json`

### 4. 주의사항

- **temperature**: 전 스크립트 0.2로 통일
- **비결정성**: LLM 응답 특성상 결과가 소폭 변동될 수 있음
- **모델 버전**: 결과는 2026년 3월 기준 모델 버전에서 생성됨
- **GPT-5.2**: `max_completion_tokens` 파라미터 사용
- **HCX-007**: thinking mode 적용 (ai_scoring: medium, crisis_scoring: enabled)
- **API 비용**: 전체 스크립트 실행 시 상당한 API 호출 비용 발생

---

## 데이터 출처

| 데이터 | 출처 | 접근 | 저장 위치 |
|--------|------|------|----------|
| WGI | [World Bank](https://info.worldbank.org/governance/wgi/) | REST API | `raw_downloads/wgi_*.json`, `wgi_full_dataset_2025.xlsx` |
| OECD DGI | [OECD](https://www.oecd.org/governance/digital-government/) | SDMX API | `raw_downloads/oecd_dgi_full.csv` |
| UN EGDI | [UN DESA](https://publicadministration.un.org/egovkb/) | 웹사이트 | `raw_downloads/un_egdi_korea_source.md` |
| 법률 원문 | [국가법령정보센터](https://www.law.go.kr) | 웹 스크래핑 | `verified/laws/` (6건) |
| 국회 의안 | [열린국회정보](https://open.assembly.go.kr) | Open API | — |
| 위기 타임라인 | 정부 보도자료·관보·법제처 | 수동 수집 | `raw_downloads/crisis_timelines.md` |

---

## 라이선스

학술 연구 목적. 인용 시 출처 명시.

```
이석민 (2026). 한국 역대 정부의 적응적 거버넌스 역량 비교.
GitHub: https://github.com/LeeSeogMin/president
```
