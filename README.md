# 한국 역대 정부 적응적 거버넌스 역량 비교 연구

> **저자**: 이석민, 한신대학교 공공인재빅데이터융합학부
> **투고 대상**: 한국행정학보
> **분석 기간**: 2003-2026 (노무현~이재명, 6개 정부)

---

## 연구 개요

6개 한국 대통령 정부의 적응적 거버넌스(adaptive governance) 역량을 비교 분석하는 학술 연구입니다. SAPD(State-based Adaptive Policy Design) 이론과 실증 검증을 통합한 논문입니다.

### 핵심 방법론: 3층 하이브리드 구조

```
제1층: Action Inventory — 객관적 사실만 기록 (점수 없음)
제2층: T/I/D/E Attribution — 추세(T)/의도(I)/표류(D)/외부(E) 귀인 분류
제3층: Blind AI Validation — 5개 AI 모델 블라인드 검증
```

### 분석 대상

| 정부 | 임기 | ACW 총점 |
|------|------|:-------:|
| 문재인 | 2017-2022 (5년) | +17 |
| 이재명 (잠정) | 2025- (~1년) | +15 |
| 이명박 | 2008-2013 (5년) | +11 |
| 노무현 | 2003-2008 (5년) | +4 |
| 윤석열 | 2022-2025 (~2.5년, 계엄→탄핵) | -5 |
| 박근혜 | 2013-2017 (4년, 탄핵) | -9 |

---

## 재현 방법 (Reproducibility)

### 1. 환경 설정

```bash
git clone https://github.com/LeeSeogMin/president.git
cd president
pip install -r requirements.txt
cp .env.example .env
# .env 파일에 실제 API 키 입력
```

### 2. 필요 API 키 (5개 모델)

| 모델 | 환경 변수 | 발급처 |
|------|----------|--------|
| GPT-5.2 | `OPENAI_API_KEY` | [OpenAI](https://platform.openai.com) |
| Claude Sonnet 4.6 | `ANTHROPIC_API_KEY` | [Anthropic](https://console.anthropic.com) |
| Grok-4-1 | `XAI_API_KEY` | [xAI](https://console.x.ai) |
| Gemini 3 Flash | `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com) |
| HyperCLOVA HCX-007 | `CLOVA_STUDIO_API_KEY` | [NAVER Cloud](https://www.ncloud.com/product/aiService/clovaStudio) |

### 3. 분석 스크립트 실행

#### 블라인드 T/I/D/E 검증 (제3층)
```bash
python data/scripts/blind_coding.py
```
- 입력: `data/verified/tide_attribution.md` (경계 사례 46건)
- 출력: `data/verified/blind_validation_results.md`
- 원자료: `data/raw_downloads/blind_coding_responses.json`

#### AI 행위 평가 (5모델 × 3라운드)
```bash
python data/scripts/action_evaluation.py
```
- 입력: `data/verified/tide_attribution.md` (I/D 행위)
- 출력: `data/verified/action_evaluation_results.md`
- 원자료: `data/raw_downloads/action_evaluation_raw.json`

### 4. 재현 시 주의사항

- **LLM 응답 비결정성**: 동일 프롬프트에도 모델 응답이 소폭 변동될 수 있습니다 (temperature=0.2 설정으로 최소화)
- **모델 버전 변경**: API 모델이 업데이트되면 결과가 달라질 수 있습니다. 본 연구의 원자료(`raw_downloads/`)는 2026년 3월 기준입니다
- **CLOVA 토큰 한계**: HCX-007은 출력 길이 제한으로 부분 응답이 발생할 수 있습니다
- **GPT-5.2**: `max_completion_tokens` 파라미터를 사용해야 합니다 (`max_tokens` 사용 시 오류)

---

## 데이터 구조

```
data/
├── PROJECT_SUMMARY.md              # 전체 과정·결과 종합
├── FINAL_STATUS.md                 # 최종 완료 현황
│
├── verified/                       # 검증 완료 최종 데이터 (재현의 기반)
│   ├── acw_scoring_final.md        # ACW 최종 채점 (6정부 × 22기준)
│   ├── tide_attribution.md         # T/I/D/E 귀인 분류 (전 행위)
│   ├── action_inventory.md         # 제1층: 객관적 행위 목록
│   ├── action_evaluation_results.md # AI 5모델 행위 평가 결과
│   ├── blind_validation_results.md # 블라인드 검증 결과
│   ├── bias_removal_methodology.md # 3층 하이브리드 방법론 설계서
│   ├── panel2_acw_scoring.md       # Panel 2: 이재명 지방정부 ACW
│   ├── panel2_ljm_local_gov.md     # Panel 2: 이재명 지방정부 데이터
│   │
│   ├── wgi_korea.md                # WGI 한국 시계열 (World Bank API)
│   ├── wgi_oecd_comparison.md      # OECD 38개국 WGI 비교 (DiD)
│   ├── oecd_dgi_korea.md           # OECD DGI (2019/2023/2025)
│   ├── un_egdi_korea.md            # UN EGDI (2003-2024)
│   ├── policy_lag_verified.md      # 위기 대응 Policy Lag (7건)
│   ├── inst_scoring_verified.md    # INST 법률 기반 채점
│   ├── lowi_classification.md      # 595개 국정과제 Lowi 분류
│   ├── lowi_strict_review.md       # Lowi 엄격 기준 재검토
│   ├── laws_summary.md             # 6개 법률 종합 비교
│   ├── laws/                       # 개별 법률 원문 (6건)
│   ├── assembly_bills.md           # 국회 의안 데이터
│   ├── presidential_speeches.md    # 6개 취임사 전문
│   ├── contextual_challenges.md    # 16건 시대적 난제
│   └── roh_detailed_tasks.md       # 노무현 세부과제
│
├── scripts/                        # 분석 스크립트 (재현용)
│   ├── blind_coding.py             # 블라인드 T/I/D/E 검증
│   └── action_evaluation.py        # AI 행위 평가
│
├── raw/                            # 원본 참고자료
│   ├── method.md                   # 5개 방법론 학술 근거
│   ├── source_verification_report.md
│   └── 국정과제_수집_가이드.md
│
└── raw_downloads/                  # API 원자료 (재현 검증용)
    ├── wgi_*.json                  # World Bank WGI API 응답
    ├── wgi_full_dataset_2025.xlsx  # WGI 전체 데이터셋
    ├── oecd_dgi_full.csv           # OECD DGI 전체
    ├── roh_policy_tasks_2003.pdf   # 참여정부 국정과제 원본
    ├── blind_coding_responses.json # 블라인드 검증 AI 원자료
    ├── action_evaluation_raw.json  # 행위 평가 AI 원자료
    └── ...
```

---

## 데이터 출처

| 데이터 | 출처 | 접근 방법 |
|--------|------|----------|
| WGI Government Effectiveness | [World Bank](https://info.worldbank.org/governance/wgi/) | REST API (인증 불필요) |
| OECD DGI | [OECD](https://www.oecd.org/governance/digital-government/) | SDMX API (인증 불필요) |
| UN EGDI | [UN DESA](https://publicadministration.un.org/egovkb/) | 웹사이트 (인증 불필요) |
| 법률 원문 | [국가법령정보센터](https://www.law.go.kr) | 웹 스크래핑 |
| 국회 의안 | [열린국회정보](https://open.assembly.go.kr) | Open API (인증키 필요) |
| 국정과제 | [국회도서관 국가전략포털](https://nsp.nanet.go.kr) | 웹사이트 |

---

## 방법론적 기여

1. **데이터 정직성**: AI 생성(fabricated) 데이터 판별 → 전면 폐기 → 실제 데이터 재수집
2. **3층 하이브리드**: Action Inventory → T/I/D/E → Blind AI (축적 편향 해결)
3. **Stock-Flow 분리**: 제도적 유산(stock)과 대통령 기여(flow)를 구분하는 최초 시도
4. **시대 상대 평가**: 절대 평가 + 시대적 과제 대응 + 선제적 기여 3관점
5. **정치적 중립성**: 블라인드 검증(식별률 0%), 정치적 논란 제외 원칙, Sensitivity Analysis

---

## 알려진 한계

- FG2(형평성): 데이터 부재로 미채점 (22기준 중 유일)
- 이재명 정부: 임기 ~1년 잠정 평가 (허니문 효과 포함)
- HCX-007: 토큰 한계로 부분 응답
- 인간 코더 벤치마크 부재
- Policy Lag: 정부당 1-2건 사례의 대표성 한계
- LLM 응답 비결정성으로 완전 재현 어려움 (원자료로 검증 가능)

---

## 라이선스

학술 연구 목적. 데이터 및 코드 인용 시 출처를 명시해 주세요.

```
이석민 (2026). 한국 역대 정부 적응적 거버넌스 역량 비교 연구.
GitHub: https://github.com/LeeSeogMin/president
```
