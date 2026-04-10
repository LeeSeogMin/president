# 한국 정부의 적응적 거버넌스 비교연구

축적 편향 통제를 위한 다중 지표 설계

**저자**: 이석민 (한신대학교 공공인재빅데이터융합학부)

## 연구 개요

노무현~이재명 정부(6개 행정부)의 적응적 거버넌스 역량을 다중 AI 스코어링(5모델 × 3라운드)으로 비교 평가한다. 후대 정부가 법·제도 누적으로 유리해지는 **축적 편향(accumulation bias)**을 통제하기 위해 5개 독립 지표를 설계하였다.

## 방법론

### 5개 독립 지표

| 지표 | 측정 대상 | 축적 편향 통제 방식 |
|------|----------|-------------------|
| **T/I/D/E 가중합** | 정책 행위의 변동 요인 분류 | Trend(T), External(E) 제외 후 Intentional(I)·Drift(D)만 합산 |
| **AGLI** | 적응적 거버넌스 학습 지수 | Ostrom IAD 0-4 척도, 저량(stock)-유량(flow) 분리 |
| **Lowi STRICT** | 정책 도구 유형론 | STRICT 기준 적용, 키워드 기반 분류 배제 |
| **CRS** | 위기 대응 적절성 | 3차원(인지·결정, 적절성, 집행) × 0-4 점수 |
| **WGI 잔차** | 세계은행 거버넌스 지표 | 선형 추세 제거 후 잔차 = 대통령 기여분 |

### AI 스코어링 모델 (5개)

| 모델 | 공급자 |
|------|--------|
| GPT-5.2 | OpenAI |
| Claude Sonnet 4.6 | Anthropic |
| Grok-4-1 | xAI |
| HyperCLOVA HCX-007 | NAVER Cloud |
| Gemini 3 Flash | Google |

전 스크립트 `temperature=0.2` 통일. 모델 간 Fleiss kappa로 평가자 간 신뢰도 측정.

### 블라인드 설계

- **Level 1**: 프롬프트에 정부명 미포함 (ACW/제도적 스코어링)
- **Level 2**: 정부명을 Greek 라벨(Alpha~Zeta)로 치환 (T/I/D/E, CRS)

## 프로젝트 구조

```
president/
├── README.md
├── requirements.txt
├── .env.example              # API 키 설정 템플릿
├── .gitattributes            # Git LFS 설정
│
└── data/
    ├── gov_factsheets.md     # 6개 정부 배경 팩트시트 (ai_scoring_v2.py 입력)
    │
    ├── scripts/              # Python 분석 파이프라인
    │   ├── ai_scoring_v2.py          # 핵심 스코어링 (Panel 1+2)
    │   ├── multi_round_scoring.py    # 반복 측정 (3라운드)
    │   ├── blind_coding.py           # T/I/D/E 블라인드 검증
    │   ├── blind_validation_report.py # 블라인드 검증 보고서 생성
    │   ├── crisis_scoring.py         # CRS 위기 대응 채점
    │   └── action_evaluation.py      # I/D 행위 영향 평가
    │
    ├── raw_downloads/        # 외부 원시 데이터
    │   ├── wgi_full_dataset_2025.xlsx   # World Bank WGI (Git LFS)
    │   ├── wgi_korea_*.json             # WGI 한국 지표 (7개)
    │   ├── wgi_oecd_38_GE_EST.json      # OECD 38개국 GE 비교
    │   ├── oecd_dgi_full.csv            # OECD 전자정부 지수
    │   ├── un_egdi_korea_source.md      # UN 전자정부 발전지수
    │   └── crisis_timelines.md          # 18개 위기 사례 타임라인
    │
    └── verified/             # 확정 분석 결과 (레퍼런스)
        ├── tide_attribution.md          # T/I/D/E 귀인 코딩 (수동)
        ├── tide_weighted.md             # T/I/D/E 가중합 결과
        ├── agli_scoring_v2.md           # AGLI 결과
        ├── lowi_classification.md       # Lowi 분류
        ├── lowi_strict_review.md        # Lowi STRICT 검토
        ├── lowi_validation.md           # Lowi 검증
        ├── composite_scoring.md         # 종합 점수 (Z-score, Borda)
        ├── adaptive_capacity_profile.md # ACW 6차원 프로파일
        ├── wgi_confidence.md            # WGI 잔차 분석
        ├── ljm_leadership_analysis.md   # 이재명 리더십 분석
        ├── panel2_ljm_local_gov.md      # Panel 2 결과
        ├── tide_governor_ljm.md         # 지사 T/I/D/E
        ├── laws_summary.md              # 법률 요약
        └── laws/                        # 법률 원문 6건
```

## 재현 방법

### 1. 환경 설정

```bash
git clone https://github.com/LeeSeogMin/adaptive-governance.git
cd adaptive-governance

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. API 키 설정

`.env.example`을 복사하여 `.env` 파일을 생성하고, 5개 모델의 API 키를 입력한다.

```bash
cp .env.example .env
# .env 파일을 편집하여 API 키 입력
```

필요한 API 키:
- OpenAI (GPT-5.2)
- Anthropic (Claude Sonnet 4.6)
- xAI (Grok-4-1)
- Google (Gemini 3 Flash)
- NAVER Cloud (HyperCLOVA HCX-007)

### 3. 스크립트 실행 순서

모든 스크립트는 `data/scripts/` 디렉토리에서 실행한다.

```bash
cd data/scripts
```

| 순서 | 스크립트 | 설명 | 주요 출력 |
|:----:|----------|------|----------|
| 1 | `python ai_scoring_v2.py` | ACW·제도적·Lowi 스코어링 (5모델, Panel 1+2) | `tables/scoring_v2_raw.json` |
| 2 | `python multi_round_scoring.py` | 반복 측정 안정성 (라운드 2-3) | `tables/scoring_v2_5round_avg.json` |
| 3 | `python blind_coding.py` | T/I/D/E 경계 사례 블라인드 검증 | `../raw_downloads/blind_coding_responses.json` |
| 4 | `python blind_validation_report.py` | Krippendorff alpha 산출 | `../verified/blind_validation_results.md` |
| 5 | `python crisis_scoring.py` | 18개 위기 사례 대응 채점 | `../verified/crisis_response_score.md` |
| 6 | `python action_evaluation.py` | I/D 행위 적응적 영향 평가 | `../raw_downloads/action_evaluation_raw.json` |

#### 주요 실행 옵션

```bash
# ai_scoring_v2.py
python ai_scoring_v2.py --panel 1              # Panel 1만 실행
python ai_scoring_v2.py --panel 2              # Panel 2만 실행
python ai_scoring_v2.py --models gpt gemini    # 특정 모델만
python ai_scoring_v2.py --reuse-panel1         # Panel 1 결과 재사용

# multi_round_scoring.py
python multi_round_scoring.py --round 2        # 2라운드만
python multi_round_scoring.py --aggregate-only # 집계만 (API 호출 없음)
```

### 4. `data/verified/` 디렉토리

이 디렉토리의 파일들은 스크립트 실행 결과를 연구자가 검토·검증하여 정리한 **레퍼런스 결과**이다. 스크립트를 재실행하면 AI 모델의 비결정적 특성상 수치가 소폭 변동할 수 있으나, 전체 순위 패턴은 안정적으로 재현된다.

## 데이터 출처

| 데이터 | 출처 | 파일 |
|--------|------|------|
| World Governance Indicators | World Bank | `wgi_full_dataset_2025.xlsx` |
| Digital Government Index | OECD | `oecd_dgi_full.csv` |
| E-Government Development Index | UN DESA | `un_egdi_korea_source.md` |
| 위기 사례 타임라인 | 연구자 수집 | `crisis_timelines.md` |
| 법률 원문 | 국가법령정보센터 | `verified/laws/` |

## 체계적 한계

- **LLM 방법론**: AI 모델을 독립 코더로 활용하는 방법론은 한국 학계에서 전례가 없으며, 인간 코더 벤치마크가 부재하다.
- **허니문 효과**: 이재명 정부(임기 0.8년)는 잠정 평가이며, 임기 초기 상향 편향이 존재할 수 있다.
- **AI 비결정성**: temperature=0.2를 적용하였으나 동일 프롬프트에 대한 응답이 완전히 동일하지 않을 수 있다. 3라운드 반복 측정과 5모델 교차 검증으로 안정성을 확보하였다.

## 라이선스

학술 연구 목적으로 공개한다. 인용 시 아래를 사용한다:

> 이석민. (2026). 한국 정부의 적응적 거버넌스 비교연구: 축적 편향 통제를 위한 다중 지표 설계. 한신대학교.
