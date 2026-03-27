# 한국 역대 정부 적응적 거버넌스 역량 비교 연구

> **저자**: 이석민, 한신대학교 공공인재빅데이터융합학부
> **발표**: 학술대회 working paper (2편)
> **분석 기간**: 2003-2026 (노무현~이재명, 6개 정부)

---

## 연구 개요

6개 한국 대통령 정부의 적응적 거버넌스(adaptive governance) 역량을 비교 분석하는 학술 연구입니다.

### 2편 구성

**Paper A (실증, 발표 1순위)**: 한국 역대 정부의 적응적 거버넌스 역량 비교 — T/I/D/E 귀인 분석과 법적 변곡점을 중심으로
**Paper B (이론, 발표 2순위)**: 상태 기반 적응형 정책 설계(SAPD) — AI 시대 정책 아키텍처

### 핵심 방법론

**T/I/D/E 귀인 분석** (본 연구의 핵심 기여)
```
T (Trend)       — 시대적 추세, 어떤 대통령이든 발생 → 비교에서 제외
I (Intentional)  — 대통령의 의도적 결정 → 비교 대상
D (Drift)        — 제도 존재하나 작동 실패 → 비교 대상
E (External)     — 외부 충격 → 비교에서 제외
```

이를 통해 "제도적 유산(stock)"과 "대통령 실제 기여(flow)"를 분리하여, 후대 정부의 구조적 유리함(축적 편향)을 통제합니다.

### 분석 프레임워크

본 연구는 **체계적 탐색 분석(systematic exploratory analysis)**으로, 강한 인과적 비교가 아닌 제도적 패턴과 분기점을 식별하는 것을 목표로 합니다.

**3개 핵심 비교축** (ACW 총점 대체):
1. **제도 분기점 분석** — 어떤 법률/제도가 언제 만들어졌는가
2. **T/I/D/E 귀속 프로파일** — 각 대통령의 실제 기여 패턴
3. **Lowi 정책 설계 분석** — 적응적 도구 채택 (엄격 기준)

**보조 지표**: ACW 차원별 프로파일, WGI 디트렌딩(탐색적), OECD DiD 비교

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

#### 블라인드 T/I/D/E 검증
```bash
python data/scripts/blind_coding.py
```

#### AI 행위 평가
```bash
python data/scripts/action_evaluation.py
```

### 4. 재현 시 주의사항

- LLM 응답 비결정성: 동일 프롬프트에도 소폭 변동 (temperature=0.2로 최소화)
- 모델 버전: API 업데이트 시 결과 변동 가능. 원자료(`raw_downloads/`)는 2026년 3월 기준
- GPT-5.2: `max_completion_tokens` 사용 필수
- CLOVA HCX-007: 출력 토큰 한계로 배치 처리 필요

---

## 데이터 구조

```
data/
├── PROJECT_SUMMARY.md              # 전체 과정·결과 종합
├── FINAL_STATUS.md                 # 최종 완료 현황
│
├── verified/                       # 검증 완료 최종 데이터
│   ├── ── 핵심 분석 결과 ──
│   ├── tide_attribution.md         # ★ T/I/D/E 귀인 분류 (핵심 1차 비교)
│   ├── acw_scoring_final.md        # ACW 채점 (보조 종합지표)
│   ├── action_inventory.md         # 제1층: 객관적 행위 목록
│   ├── action_evaluation_results.md # AI 5모델 행위 방향성 검증
│   ├── blind_validation_results.md # 블라인드 검증 결과
│   ├── lowi_strict_review.md       # Lowi 엄격 기준 재검토
│   │
│   ├── ── 방법론 ──
│   ├── bias_removal_methodology.md # 3층 하이브리드 기본 설계
│   ├── methodology_restructuring_proposal.md # 방법론 재구조화
│   ├── acw_doublecounting_resolution.md # ACW 이중계상 해소
│   ├── ti_quantification_rules.md  # T+I 정량화 규칙
│   │
│   ├── ── 수집 데이터 ──
│   ├── wgi_korea.md                # WGI 한국 시계열
│   ├── wgi_oecd_comparison.md      # OECD 38개국 비교 (DiD)
│   ├── oecd_dgi_korea.md           # OECD DGI
│   ├── un_egdi_korea.md            # UN EGDI
│   ├── policy_lag_verified.md      # 위기 대응 Policy Lag (7건)
│   ├── inst_scoring_verified.md    # INST 법률 기반 채점
│   ├── lowi_classification.md      # 595개 국정과제 Lowi 분류
│   ├── laws/ (6개 법률)            # 법률 원문
│   ├── laws_summary.md             # 법률 종합 비교
│   ├── assembly_bills.md           # 국회 의안 데이터
│   ├── presidential_speeches.md    # 6개 취임사 전문
│   ├── contextual_challenges.md    # 16건 시대적 난제
│   ├── panel2_acw_scoring.md       # Panel 2: 이재명 지방정부
│   ├── panel2_ljm_local_gov.md     # Panel 2 원시 데이터
│   └── roh_detailed_tasks.md       # 노무현 세부과제
│
├── scripts/                        # 재현용 분석 스크립트
│   ├── blind_coding.py             # 블라인드 T/I/D/E 검증
│   └── action_evaluation.py        # AI 행위 평가
│
├── raw/                            # 원본 참고자료
│   ├── method.md                   # 5개 방법론 학술 근거
│   └── 국정과제_수집_가이드.md
│
└── raw_downloads/                  # API 원자료 (재현 검증용)
    ├── wgi_*.json                  # World Bank WGI API
    ├── oecd_dgi_full.csv           # OECD DGI
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
| UN EGDI | [UN DESA](https://publicadministration.un.org/egovkb/) | 웹사이트 |
| 법률 원문 | [국가법령정보센터](https://www.law.go.kr) | 웹 스크래핑 |
| 국회 의안 | [열린국회정보](https://open.assembly.go.kr) | Open API (인증키 필요) |

---

## 방법론적 기여

1. **T/I/D/E 귀인 분석**: 제도적 유산(stock)과 대통령 기여(flow)를 분리하는 최초 시도
2. **1사건-1기준 원칙**: ACW 이중계상 해소
3. **Lowi 엄격 재분류**: 키워드 매칭 vs 실질적 적응 메커니즘 구분
4. **Stock-Flow 이중 보고**: INST 법률 기반 채점
5. **시대 상대 평가**: 절대 + 시대적 과제 대응 + 선제적 기여 3관점

---

## 알려진 한계

- 체계적 탐색 분석으로, 강한 인과적 비교를 주장하지 않음
- ACW는 보조 종합지표이며, 총점 순위를 주결론으로 제시하지 않음
- 이재명 정부: 임기 ~1년 잠정 평가 (허니문 효과 포함)
- WGI는 인식(perception) 지표, 시차 효과 존재
- AI 검증은 보조 도구 (독립적 ground truth 아님)
- Policy Lag: 정부당 1-2건, 위기 유형 상이

---

## 라이선스

학술 연구 목적. 인용 시 출처 명시.

```
이석민 (2026). 한국 역대 정부 적응적 거버넌스 역량 비교 연구.
GitHub: https://github.com/LeeSeogMin/president
```
