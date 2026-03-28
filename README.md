# 상태 기반 적응형 정책 설계(SAPD): AI 시대 정책 아키텍처

> **저자**: 이석민, 한신대학교 공공인재빅데이터융합학부
> **분석 기간**: 2003-2026 (노무현~이재명, 6개 정부)
> **방법론**: 개념적 분석 + 다중 AI 스코어링 (5모델 × 5라운드)

---

## 프로젝트 구조

```
president/
├── README.md
├── CLAUDE.md                        # AI 어시스턴트 지침
├── requirements.txt                 # Python 의존성
├── .env.example                     # API 키 템플릿
│
├── paper/                           # 논문 본체
│   ├── paper_a_draft.md             # Paper A: 실증 비교 원고
│   ├── paper_b_draft.md             # Paper B: SAPD 이론 원고
│   ├── paper_a_outline.md           # Paper A 구조
│   ├── paper_b_outline.md           # Paper B 구조
│   ├── two_paper_structure.md       # 2논문 설계 문서
│   ├── style/writing-style.md       # 한국어 학술 문체 가이드
│   ├── review/                      # 다중 LLM 리뷰
│   │   ├── paper_a/                 # Paper A 리뷰 (3모델 + 종합)
│   │   ├── paper_b/                 # Paper B 리뷰 (3모델 + 종합)
│   │   └── phase7/                  # Phase 7 리뷰 스크립트
│   └── research/                    # Phase 1-5 연구 파이프라인 아카이브
│
├── data/
│   ├── verified/                    # 최종 검증 완료 데이터 (논문의 근거)
│   │   ├── tide_weighted.md         # T/I/D/E Hall 3차수 가중합
│   │   ├── agli_scoring_v2.md       # AGLI (Ostrom IAD, 0-4)
│   │   ├── lowi_strict_review.md    # Lowi STRICT 적응적 도구 분류
│   │   ├── lowi_classification.md   # Lowi 595 국정과제 전체 분류
│   │   ├── lowi_validation.md       # Lowi 코딩 검증 (kappa=0.898)
│   │   ├── wgi_confidence.md        # WGI 추세제거 잔차 + 신뢰구간
│   │   ├── policy_lag_v2.md         # Policy Lag (OECD Agility, 20건)
│   │   ├── crisis_response_score.md # CRS (5 AI 블라인드 채점)
│   │   ├── composite_scoring.md     # 종합 점수 (3방법 × 복수 가중치)
│   │   ├── adaptive_capacity_profile.md # 적응역량 프로파일 (비가산)
│   │   └── laws/                    # 6개 핵심 법률 원문
│   │
│   ├── raw_downloads/               # 원시 데이터 (API 응답, 스크래핑 등)
│   │
│   ├── scripts/                     # Python 분석 스크립트
│   │   ├── ai_scoring_v2.py         # 5모델 AI 스코어링 (ACW/제도/Lowi)
│   │   ├── multi_round_scoring.py   # 5라운드 반복 측정
│   │   ├── blind_coding.py          # T/I/D/E 블라인드 검증
│   │   ├── crisis_scoring.py        # CRS 채점 (위기 × 5모델)
│   │   └── action_evaluation.py     # 행위 평가 (적응적 영향 + 시간민감도)
│   │
│   └── raw_deprecated/              # 구버전·중간 산출물 (아카이브)
```

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

### 3. 스크립트 실행

스크립트 간 의존관계가 있으므로 아래 순서대로 실행합니다.

#### Step 1: 핵심 AI 스코어링 (ACW/제도/Lowi)

```bash
python data/scripts/ai_scoring_v2.py
```

5개 모델이 6개 정부의 ACW·제도적 메커니즘·Lowi 유형을 채점합니다.
출력: `data/raw_downloads/` (원시 JSON) + `data/verified/` (검증 결과 마크다운)

옵션:
- `--panel 1` / `--panel 2`: 특정 패널만 실행
- `--models gpt claude`: 특정 모델만 실행
- `--reuse-panel1`: 기존 Panel 1 결과 재사용

#### Step 2: 다중 라운드 반복 측정

```bash
python data/scripts/multi_round_scoring.py
```

Step 1의 1회차 결과를 기반으로 4회 추가 측정 (총 5라운드)하여 평균을 산출합니다.
출력: `data/raw_downloads/` (라운드별 JSON)

옵션:
- `--round 3`: 특정 라운드만 실행
- `--aggregate-only`: 기존 결과 집계만 수행
- `--models gpt claude`: 특정 모델만 실행

#### Step 3: T/I/D/E 블라인드 검증

```bash
python data/scripts/blind_coding.py
```

`data/verified/tide_attribution.md`의 경계 사례를 블라인드 처리 후 5개 모델 × 3라운드로 검증합니다.
출력: `data/verified/blind_validation_results.md`

#### Step 4: 위기 대응 채점 (CRS)

```bash
python data/scripts/crisis_scoring.py
```

`data/raw_downloads/crisis_timelines.md`의 위기 사례를 블라인드 처리 후 5개 모델이 3차원(인지·적절성·집행) × 0-4로 채점합니다.
출력: `data/verified/crisis_response_score.md`

옵션: `--models gpt claude`

#### Step 5: 행위 평가

```bash
python data/scripts/action_evaluation.py
```

I/D 유형 행위의 적응적 거버넌스 영향(+1/0/-1)과 시간민감도(2003 vs 2023)를 평가합니다.
출력: `data/verified/action_evaluation_results.md`, `data/raw_downloads/action_evaluation_raw.json`

### 4. 주의사항

- **비결정성**: LLM 응답 특성상 결과가 소폭 변동될 수 있음 (temperature=0.2~0.3)
- **모델 버전**: 결과는 2026년 3월 기준 모델 버전에서 생성됨. 모델 업데이트 시 변동 가능
- **GPT-5.2**: `max_completion_tokens` 파라미터 사용 (기존 `max_tokens` 아님)
- **HCX-007**: 출력 토큰 한계로 배치 처리 적용됨
- **API 비용**: 전체 스크립트 실행 시 상당한 API 호출 비용 발생

---

## 데이터 출처

| 데이터 | 출처 | 접근 |
|--------|------|------|
| WGI | [World Bank](https://info.worldbank.org/governance/wgi/) | REST API |
| OECD DGI | [OECD](https://www.oecd.org/governance/digital-government/) | SDMX API |
| UN EGDI | [UN DESA](https://publicadministration.un.org/egovkb/) | 웹사이트 |
| 법률 원문 | [국가법령정보센터](https://www.law.go.kr) | 웹 스크래핑 |
| 국회 의안 | [열린국회정보](https://open.assembly.go.kr) | Open API |

---

## 라이선스

학술 연구 목적. 인용 시 출처 명시.

```
이석민 (2026). 상태 기반 적응형 정책 설계(SAPD): AI 시대 정책 아키텍처.
GitHub: https://github.com/LeeSeogMin/president
```
