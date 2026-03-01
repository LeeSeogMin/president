# President 프로젝트 종합 연구 보고서

> 조사일: 2026-03-02
> 대상: `c:\Dev\president` 전체 프로젝트

---

## 1. 프로젝트 개요

이 프로젝트는 **두 개의 연관된 서브프로젝트**로 구성된 학술 연구 저장소이다.

| 서브프로젝트 | 경로 | 목적 |
|-------------|------|------|
| **SAPD** | `SAPD/` | "상태 기반 적응형 정책(State-based Adaptive Policy)" 이론 논문 작성 |
| **LJM** | `ljm/` | SAPD 논문 3절의 이재명 정부 "적응형 행정" 분류를 다중 방법론으로 객관적 검증 |

**저자**: 이석민, 한신대학교 공공인재빅데이터융합학부
**타겟 저널**: 한국행정학보, 행정논총, 한국정책학회보 등 국내 학술지
**논문 언어**: 국문 (Korean)

---

## 2. 프로젝트 구조

```
president/
├── .env                          # API 키 (OpenAI, Anthropic, xAI, Gemini, NCP/CLOVA)
├── .gitignore
├── SAPD/                         # 서브프로젝트 1: SAPD 이론 논문
│   ├── CLAUDE.md                 # 프로젝트 메모리 파일
│   ├── context.md                # 세션 추적
│   ├── todo.md                   # 할 일 목록
│   ├── ai-docs/
│   │   └── writing-style.md      # 학술 글쓰기 스타일 가이드
│   ├── docs/
│   │   ├── existing_content_index.md  # 재활용 콘텐츠 인덱스
│   │   └── paper_proposal.md          # 논문 제안서
│   ├── specs/workflows/
│   │   └── full-pipeline.md      # 10-Phase 파이프라인 정의
│   ├── phase1_literature/        # Phase 1: 문헌 검토
│   │   ├── literature_review.md
│   │   ├── research_gaps.md
│   │   └── theoretical_positioning.md
│   ├── phase2_design/            # Phase 2: 논증 설계
│   │   ├── analytical_strategy.md
│   │   ├── argumentative_design.md (v1~v3)
│   │   └── concept_definitions.md
│   ├── phase3_sources/           # Phase 3: 소스 자료 구축
│   │   ├── case_materials/palantir_case.md
│   │   ├── concept_mapping.md
│   │   ├── framework_taxonomy.md
│   │   └── paradigm_comparison.md
│   ├── phase4_analysis/          # Phase 4: 비교 프레임워크 분석
│   │   ├── architecture_analysis.md
│   │   ├── framework_differentiation.md
│   │   ├── isomorphism_analysis.md
│   │   └── paradigm_analysis.md
│   ├── phase5_validation/        # Phase 5: 검증
│   │   ├── boundary_analysis.md
│   │   ├── consistency_check.md
│   │   ├── counter_arguments.md
│   │   └── cross_domain_validation.md
│   ├── phase6_drafting/          # Phase 6: 논문 초안
│   │   └── paper_draft_v1~v3.md
│   ├── phase7_review/            # Phase 7: 다중 LLM 리뷰 (3라운드)
│   │   ├── run_review.py
│   │   ├── review_v3_script.py
│   │   ├── reviews/              # 라운드 1
│   │   ├── reviews_v2/           # 라운드 2
│   │   └── reviews_v3/           # 라운드 3
│   └── phase10_submission/       # Phase 10: 투고 패키지
│       ├── paper_final_v1~v5.md
│       ├── paper_final_v1~v3.hwpx
│       ├── cover_letter_v1~v2.md
│       ├── comparison_analysis.md
│       └── submission_checklist_v1~v2.md
│
└── ljm/                          # 서브프로젝트 2: 이재명 정부 적응형 행정 검증
    ├── context.md                # 프로젝트 개요
    ├── todo.md                   # 할 일 목록
    ├── analysis_main.md          # 단일 코더 분석 본문 (5개 방법론)
    ├── full_report.md            # 최종 종합 보고서
    ├── data/                     # 데이터 파일
    │   ├── acw_scoring.md        # ACW 22개 기준별 점수
    │   ├── policy_lag.md         # 위기 대응 시간 데이터
    │   ├── intl_indices.md       # WGI, EGDI, DGI 시계열
    │   ├── institutional.md      # 제도적 구조 비교
    │   ├── ljm_local_context.md  # Panel 2 팩트시트
    │   └── method.md             # 방법론 학술적 근거
    ├── ai_scoring.py             # v1: 4모델 단일 라운드 스코어링
    ├── ai_scoring_v2.py          # v2: 5모델 2패널 스코어링 (핵심 라이브러리)
    ├── multi_round_scoring.py    # 5라운드 반복 측정 시스템
    ├── method_consult.py         # AI 방법론 적용 가능성 컨설팅
    ├── fix_clova_ljm.py          # CLOVA 전점 0점 이상치 수정
    ├── fix_anomalies.py          # 3건 이상치 수정
    ├── fix_ljm_president.py      # 이재명 대통령 전체 재평가
    └── tables/                   # 결과 데이터
        ├── acw_raw_results.json
        ├── inst_raw_results.json
        ├── scoring_v2_raw.json
        ├── scoring_v2_5round_avg.json
        ├── completion_matrix.json
        ├── reliability_summary.json
        ├── method_consult_raw.json
        ├── rounds/round_1~5.json
        ├── multi_ai_scoring_report.md
        ├── scoring_v2_report.md
        ├── capacity_trajectory.md
        └── method_consult_report.md
```

---

## 3. SAPD 서브프로젝트 상세 분석

### 3.1 핵심 논제

**증거 기반 정책(Evidence-Based Policy, EBP)의 구조적 한계를 극복하는 새로운 정책 패러다임으로서, '상태 기반 적응형 정책(State-based Adaptive Policy)'은 어떤 이론적 기초와 설계 아키텍처를 통해 실시간 적응형 거버넌스를 구현할 수 있는가?**

핵심 주장: EBP의 시간 지연(time lag)은 구현상의 문제가 아닌 **인식론적 설계의 구조적 결함**이며, 이를 해결하기 위해서는 정책을 "사후 평가되는 이산적 개입"에서 **"연속적 상태 전이 함수"**로 재정의하는 패러다임 전환이 필요하다.

### 3.2 핵심 공식

```
State(t) → Decision(t) = f(State(t)) → System Response → State(t+1) → [반복]
```

시간 지연 분해:
```
τ_total = τ_detection + τ_collection + τ_analysis + τ_reporting + τ_deliberation + τ_implementation
```

### 3.3 세 가지 핵심 명제

| 명제 | 내용 |
|------|------|
| **P1** | EBP의 시간 지연은 구조적 아키텍처 결함으로, 패러다임 수준의 대응 필요 |
| **P2** | 정책 시스템은 상태 전이 함수로 모델링 가능하며, 연속적 적응을 구현 |
| **P3** | SAPD의 5단계 아키텍처는 적응형 정책 구현을 위한 충분한 설계 명세 제공 |

### 3.4 SAPD 5-Layer 아키텍처

| Layer | 이름 | 기능 | 공식 |
|-------|------|------|------|
| **L1** | 문제 구조화 | 상태 공간 Ω = {S, E, B} 정의 | State space definition |
| **L2** | 전략 구조화 | 목표 함수, 전략 대안, 평가 기준 정의 | min \|\|State(t) - S*\|\| |
| **L3** | 의사결정 아키텍처 | 의사결정 규칙, 파라미터, 인간 개입 조건 | Decision(t) = f(State(t); θ) |
| **L4** | 데이터 통합 | 실시간 상태 관측, AI 통합 | State_obs(t) = h(Data(t)) + ε |
| **L5** | 평가 및 적응적 피드백 | 지속적 격차 측정, 3단계 적응 | Gap(t) = \|\|State(t) - S*\|\| |

**3단계 적응 메커니즘**:
- **1차 적응 (운영)**: L5 → L3. 기존 규칙 내 파라미터 θ 조정 (예: 급여 금액 조정)
- **2차 적응 (전략)**: L5 → L2. 목표와 전략 수정 (예: "디지털 뉴딜" → "AI 전환" 프레이밍)
- **3차 적응 (구조)**: L5 → L1. 문제 자체 재정의 (예: 사후 평가 → 실시간 데이터 행정)

### 3.5 10-Phase 파이프라인 실행 결과

| Phase | 이름 | 핵심 산출물 | 상태 |
|-------|------|------------|------|
| 0 | 인프라 구축 | CLAUDE.md, context.md, writing-style.md | 완료 |
| 1 | 문헌 검토 | literature_review.md, research_gaps.md, theoretical_positioning.md | 완료 |
| 2 | 논증 설계 | argumentative_design_v3.md, concept_definitions.md | 완료 |
| 3 | 소스 자료 구축 | palantir_case.md, framework_taxonomy.md, paradigm_comparison.md | 완료 |
| 4 | 비교 분석 | architecture_analysis.md, isomorphism_analysis.md, paradigm_analysis.md | 완료 |
| 5 | 검증 | boundary_analysis.md, counter_arguments.md, cross_domain_validation.md | 완료 |
| 6 | 논문 초안 | paper_draft_v1~v3.md | 완료 |
| 7 | 다중 LLM 리뷰 | 3라운드 × 3모델 리뷰 + 종합 | 완료 |
| 8 | AI 탐지 | (명시적 문서 없음) | 불명확 |
| 9 | 전문 편집 | paper_final 버전 반영 | 완료 |
| 10 | 투고 패키지 | paper_final_v5.md, cover_letter_v2.md | 거의 완료 |

### 3.6 다중 LLM 리뷰 프로세스 (Phase 7)

**사용 모델**: GPT-5.2, Grok-4, Claude Sonnet 4.6
**설정**: temperature 0.3, max_tokens 8192, 한국행정학보 심사위원 역할 프롬프트

#### 3라운드 리뷰 진행 과정

| 라운드 | 대상 | 공통 지적 사항 |
|--------|------|--------------|
| **1** | paper_draft_v1 (순수 이론) | 한국 맥락 부재, 약한 경험적 근거, 누락 문헌 |
| **2** | paper_draft_v2 (한국 사례 추가) | 이론적 독창성 논증 불충분, 팔란티어 방법론적 한계, 수학적 형식화 상태 모호 |
| **3** | paper_draft_v3 (이재명 명명) | **정치적 편향 리스크** (3개 모델 모두 지적), SAPD 독창성, 경험적 증거, ∇_θ J 표기 문제 |

#### 핵심 프레이밍 결정: 이재명 직접 명명

- v1: 순수 이론, 특정 정부 미명시
- v2: 한국 사례 포함, 익명화 ("한국 정부")
- **v3/최종: 이재명 정부 직접 명명** → 3개 AI 모두 최고 위험 결정으로 지적
- 최종 논문: 명명 유지 + 사례 선정 논리, 교차 정부 비교, 평가적 언어 완화로 대응

### 3.7 최종 논문 구조 (paper_final_v5.md)

**제목**: "상태 기반 적응형 정책: 한국 행정 혁신의 구조적 한계와 AI 기반 설계 프레임워크"

| 절 | 내용 |
|----|------|
| 1. 서론 | EBP 한계, 한국 적응형 행정, 연구 질문, 3대 기여 |
| 2. 이론적 배경 | EBP 4축 비판, 적응적 거버넌스, 시스템 다이내믹스, 정책 학습, 알고리즘 거버넌스, **7개 프레임워크 비교표** |
| 3. 한국 적응형 행정 | COVID-19 대응, 기본소득, AI 기본법, 구조적 한계 진단 |
| 4. 연구 방법론 | 개념적 연구(Jaakkola 2020), 4개 분석 방법 |
| 5. 상태 기반 적응형 정책 | 패러다임 정의, 공식의 "설계 언어" 지위, EBP 비교 |
| 6. SAPD 프레임워크 | 5-Layer 아키텍처, 거버넌스 설계, 3단계 적응, 수식 |
| 7. 이중 타당성 분석 | 팔란티어 + 대안 플랫폼, 한국 사례 역매핑 |
| 8. 논의 | 독창성 요소, 공공가치 + 의사결정유형별 설계, 한계, 반론 |
| 9. 결론 | 3대 기여, 한계, 향후 연구 |

**분량**: 약 28,000자, 참고문헌 50편 이상 (한국어 학술 논문 15편 포함)

### 3.8 이중 타당성 분석

| 타당성 유형 | 방법 | 근거 |
|-------------|------|------|
| **기술적 타당성** | 구조적 동형성 분석 | SAPD 5-Layer와 팔란티어 Foundry/AIP/Ontology 스택 간 동형 사상 φ |
| **정책적 타당성** | 역매핑 분석 | 한국 정부의 적응적 행정 관행을 SAPD 레이어에 매핑 |

### 3.9 SAPD 잔여 과제

- 영문 초록 및 키워드 미작성
- HWPX 형식 변환 (한국행정학보 투고 요건)
- 익명 심사 버전 준비
- 학술지 온라인 투고 시스템 업로드

---

## 4. LJM 서브프로젝트 상세 분석

### 4.1 연구 목적

SAPD 논문(paper_final_v5.md) 3절의 이재명 정부 "적응형 행정" 분류를 **5가지 방법론 × 다중 AI 모델**로 객관적 검증

### 4.2 비교 대상: 6개 대한민국 정부

| 정부 | 기간 | 성격 |
|------|------|------|
| 노무현 | 2003-2008 | 진보 |
| 이명박 | 2008-2013 | 보수 |
| 박근혜 | 2013-2017 | 보수 |
| 문재인 | 2017-2022 | 진보 |
| 윤석열 | 2022-2025 | 보수 |
| 이재명 | 2025- | 진보 |

### 4.3 5가지 분석 방법론

| # | 방법 | 근거 문헌 | 측정 내용 |
|---|------|----------|----------|
| A | **Adaptive Capacity Wheel (ACW)** | Gupta et al. (2010) | 6개 차원, 22개 기준, -2~+2 점수 |
| B | **Policy Lag 정량 분석** | Friedman (1960), OECD (2021) | 인지·결정·실행 지연(일 단위) |
| C | **국제 지표 시계열** | WGI, UN EGDI, OECD DGI | 정부효과성, 전자정부, 디지털정부 |
| D | **제도적 적응 메커니즘** | Argyris & Schon (1978) | D1-D4 4개 차원, 0-2점 |
| E | **국정과제 유형 분류** | Lowi (1972), Schneider & Ingram | 적응적 도구 비율 산출 |

**삼각검증(Triangulation)**: Denzin (1978) 기반, 3개 이상 방법론 수렴 시 분류 지지

### 4.4 다중 AI 스코어링 시스템

#### 사용 모델 (5개)

| 모델 | 버전 | 특성 |
|------|------|------|
| GPT | 5.2 | 가장 보수적 점수 |
| Claude | Sonnet 4.6 | 가장 안정적 (std 0.26) |
| Grok | 4-1 | 중간 수준 |
| HyperCLOVA | HCX-007 | 가장 불안정 (std 0.46), 한국 특화 |
| Gemini | 3 Flash | 가장 관대한 점수 |

#### 2-패널 설계

| 패널 | 대상 | 방법 |
|------|------|------|
| **Panel 1** | 6개 중앙정부 | ACW 22기준 + INST 4차원 |
| **Panel 2** | 이재명 지방정부 (성남시장, 경기도지사) | ACW 서브휠 + INST 기능적 동등성 + Lowi 분류 |

#### 버전 진화

- **V1**: 4모델, 단일 라운드, 단일 패널 → 이재명 ACW +0.20 (3개 모델 0점)
- **V2**: 5모델, 5라운드 반복 측정, 2패널 → 이재명 ACW +1.12 (1위)

#### 핵심 기술적 혁신

1. **판단 유보 금지 지시문**: 0점을 "평가 불가"로 사용하는 것을 명시적 금지
2. **연속성 기반 평가 지시문**: 초기 정부에 대해 지방정부 경력의 정책 연속성으로 평가
3. **대량 점수 거부 검증**: 80% 이상 0점 또는 동일 점수 자동 거부 및 재시도
4. **5라운드 평균화**: 단일 시행 분산 감소, 기준별 표준편차 보고
5. **증분 저장**: 각 API 호출 후 저장, 충돌 복구 지원

### 4.5 Python 스크립트 아키텍처

```
ai_scoring.py (v1, 4모델)       method_consult.py (방법론 컨설팅)
      │                                │
      ▼                                ▼
ai_scoring_v2.py (v2, 5모델, 핵심 라이브러리) ◄── 컨설팅 결과로 Panel 2 설계 반영
      │
      ▼
multi_round_scoring.py (5라운드 반복 측정)
      │
      ├── fix_clova_ljm.py        (CLOVA 전점 0점 수정)
      ├── fix_anomalies.py        (3건 이상치 수정)
      ├── fix_ljm_president.py    (이재명 대통령 전면 재평가)
      │
      ▼
출력: scoring_v2_raw.json → scoring_v2_5round_avg.json
      scoring_v2_report.md → full_report.md
```

**주요 아키텍처 패턴**:
- `ai_scoring_v2.py`가 공유 라이브러리 역할 (ACW_CRITERIA, INST_DIMENSIONS, API 호출 함수 export)
- 모든 스크립트 증분 저장(incremental persistence)으로 충돌 복구 가능
- 다단계 JSON 추출: 정규식 폴백, 꼬리 쉼표·미닫힘 괄호·오타 자동 수정
- 지수 백오프 (3초~48초)

### 4.6 핵심 분석 결과

#### ACW 종합 순위 (다중 AI 합의, Panel 1)

| 순위 | 정부 | ACW 합의 점수 | 특이사항 |
|------|------|-------------|---------|
| 1 | **이재명** | **+1.12** | 단일 코더 +1.36, 가장 높은 적응적 도구 비율 |
| 2 | 노무현 | +0.94 | 분권화, 전자정부, 참여적 거버넌스 |
| 3 | 문재인 | +0.54 | INST 최고 (6.8/8), COVID-19 최빠른 대응 |
| 4 | 이명박 | -0.23 | EGDI 세계 1위 달성, WGI 하락 |
| 5 | 윤석열 | -0.34 | 모델 간 불일치 최대 (범위 0.99) |
| 6 | 박근혜 | -0.75 | 제도적 점수 최저 |

#### Panel 2: 이재명 지방정부 ACW

| 역할 | ACW 서브휠 점수 | 기준 수 |
|------|----------------|---------|
| 성남시장 | +1.26 (→ 합의 +1.40) | 19 |
| 경기도지사 | +1.44 (→ 합의 +1.55) | 20 |

#### 역량 궤적 (이재명 3역할 비교)

성남시장 +1.41 → 경기도지사 +1.61 (최고) → 대통령 +1.40

- Le1 (비전), Le2 (기업가적 리더십): 전 역할 2.0 만점 유지
- Le3 (협력적 리더십): 전 역할에서 일관되게 최저 점수

#### 모델별 신뢰도

| 지표 | V1 | V2 (5라운드) |
|------|-----|-------------|
| ACW Fleiss' κ | 0.255 (공정) | 0.333 (공정) |
| INST Fleiss' κ | 0.272 (공정) | - |

- Claude: 가장 안정적 (std 0.26)
- CLOVA: 가장 불안정 (std 0.46), 가장 많은 수동 개입 필요
- GPT: 체계적 저평가 경향
- Gemini: 체계적 고평가 경향

#### 주요 발견사항

1. **진보-보수 거버넌스 분리**: 진보 정부(노무현, 문재인, 이재명)가 보수 정부(이명박, 박근혜, 윤석열)를 거의 모든 방법에서 능가 — 인간·AI 스코어링 모두 일관
2. **문재인 ACW-INST 괴리**: INST 최고(6.8/8)이나 ACW 3위(+0.54) → 강한 제도 설계이나 유연성/다양성 부족
3. **윤석열 평가 난이도**: 모델 간 불일치 최대 → 거버넌스 특성이 모호하거나 논쟁적
4. **이재명 협력적 리더십 결핍 (Le3)**: 전 역할·전 모델에서 일관 → 측정 잡음 아닌 실제 특성

### 4.7 LJM과 SAPD 논문의 연결

LJM 서브프로젝트는 SAPD 논문 3절을 직접 검증하며, 다음을 제공:
- 5개 삼각검증 방법론을 통한 정량적 증거
- 다중 AI 검증으로 단일 연구자 편향 감소
- 6개 행정부 역사적 비교를 통한 상대적 포지셔닝
- 지방-중앙 교차 수준 분석으로 정책 연속성 입증
- SAPD 논문에 대한 7개 구체적 수정 제안

---

## 5. 사용 기술 스택

### 5.1 API 및 모델

| 서비스 | 모델 | 용도 |
|--------|------|------|
| OpenAI | GPT-5.2 | AI 스코어링, LLM 리뷰 |
| Anthropic | Claude Sonnet 4.6 | AI 스코어링, LLM 리뷰 |
| xAI | Grok-4-1-fast-reasoning | AI 스코어링, LLM 리뷰 |
| Google | Gemini 3 Flash | AI 스코어링 (LJM만) |
| NCP | HyperCLOVA HCX-007 | AI 스코어링 (LJM만) |

### 5.2 개발 환경

- **언어**: Python 3.13
- **주요 라이브러리**: openai, anthropic, google-generativeai (추정), httpx
- **환경 관리**: .env 파일 (dotenv)
- **데이터 형식**: JSON (결과), Markdown (문서/데이터), HWPX (투고)
- **AI 보조 도구**: Claude Code (CLAUDE.md 메모리 시스템)

---

## 6. 프로젝트의 방법론적 혁신

### 6.1 AI-as-Coder 방법론
다중 LLM을 독립적 전문가 코더로 활용하여 정치학 연구의 코더 간 신뢰도를 확보하는 새로운 접근. 인간 코더 모집 없이도 inter-coder reliability를 산출할 수 있음.

### 6.2 2-패널 교차 수준 설계
동일 개인의 지방정부-중앙정부 역할을 기능적 동등성 원칙으로 비교하는 방법론적 창의성. 기존 정치학 연구에서 드문 설계.

### 6.3 판단 유보 대응 프롬프팅
LLM이 불확실한 평가에서 진정한 평가 대신 0점을 기본값으로 사용하는 현상 발견 및 대응 프롬프팅 기법 개발. AI 보조 연구의 실용적 기여.

### 6.4 10-Phase 학술 논문 파이프라인
인프라 → 문헌 검토 → 논증 설계 → 자료 구축 → 분석 → 검증 → 초안 → 다중 AI 리뷰 → 편집 → 투고 패키지의 체계적 AI 보조 논문 작성 워크플로우.

### 6.5 반복적 AI 리뷰-수정 루프
3라운드 × 3모델 리뷰 결과를 체계적으로 반영하는 생산적 인간-AI 피드백 루프. 각 라운드의 비평이 다음 버전에 구체적으로 반영됨.

---

## 7. 식별된 이슈 및 한계

### 7.1 SAPD 프로젝트

| 이슈 | 설명 |
|------|------|
| **경험적 검증 부재** | 3라운드 모든 리뷰어가 경험적 테스트 부재 지적. 개념적 기여에 머무름 |
| **팔란티어 참조의 한계** | (a) 한국 공공행정 미사용, (b) 감시/시민자유 논란, (c) 추상적 아키텍처 수준의 동형성 |
| **수학적 형식화 긴장** | ∇_θ J 표기의 사회과학 논문 내 위상 모호 → "설계 언어"로 재정의 |
| **정치적 편향 리스크** | 현직 대통령 직접 명명 → 학술적 객관성 의문 가능 |
| **주장 범위 과대** | 일부 절에서 SAPD를 EBP 보완이 아닌 대체로 읽힐 수 있음 |

### 7.2 LJM 프로젝트

| 이슈 | 설명 |
|------|------|
| **수정 스크립트 편향** | fix 스크립트가 다른 모델 점수를 참조로 제공 → 앵커링 효과 가능 |
| **CLOVA 불안정성** | HCX-007이 지속적 특별 처리 필요 → 이 유형의 평가에 부적합 가능 |
| **κ 상한선** | 공정 수준(0.333)이 달성 최고치 → LLM의 주관적 거버넌스 평가 한계 |
| **초기 정부 평가 문제** | 연속성 기반 평가가 합리적이나 "지방정부 패턴이 대통령 성과를 예측한다"는 가정 자체가 논쟁적 |
| **국제 지표 부재** | 이재명 정부 데이터 미존재 (취임 초기) |

---

## 8. 프로젝트 현재 상태 종합

| 항목 | SAPD | LJM |
|------|------|-----|
| **핵심 분석** | 완료 | 완료 |
| **논문/보고서** | paper_final_v5.md 완성 | full_report.md 완성 |
| **AI 리뷰/검증** | 3라운드 완료 | 5라운드 × 5모델 완료 |
| **투고 준비** | 거의 완료 (영문 초록, HWPX 변환 잔여) | 해당 없음 (보조 분석) |
| **todo.md 갱신** | 미갱신 (실제 진행 >> 기록) | 미갱신 |

---

## 9. 핵심 파일 빠른 참조

### SAPD 핵심 파일

| 용도 | 경로 |
|------|------|
| 프로젝트 메모리 | `SAPD/CLAUDE.md` |
| 파이프라인 정의 | `SAPD/specs/workflows/full-pipeline.md` |
| 프레임워크 핵심 정의 | `SAPD/phase4_analysis/architecture_analysis.md` |
| 개념 정의 | `SAPD/phase2_design/concept_definitions.md` |
| 패러다임 비교 | `SAPD/phase3_sources/paradigm_comparison.md` |
| 동형성 분석 | `SAPD/phase4_analysis/isomorphism_analysis.md` |
| 경계 조건 | `SAPD/phase5_validation/boundary_analysis.md` |
| 최종 리뷰 종합 | `SAPD/phase7_review/reviews_v3/review_synthesis_v3.md` |
| 리뷰 자동화 스크립트 | `SAPD/phase7_review/run_review.py` |
| **최종 논문** | **`SAPD/phase10_submission/paper_final_v5.md`** |
| 투고 체크리스트 | `SAPD/phase10_submission/submission_checklist_v2.md` |
| 커버레터 | `SAPD/phase10_submission/cover_letter_v2.md` |

### LJM 핵심 파일

| 용도 | 경로 |
|------|------|
| 단일 코더 분석 | `ljm/analysis_main.md` |
| **최종 종합 보고서** | **`ljm/full_report.md`** |
| 핵심 라이브러리 | `ljm/ai_scoring_v2.py` |
| 5라운드 측정 | `ljm/multi_round_scoring.py` |
| 방법론 컨설팅 | `ljm/method_consult.py` |
| 5라운드 평균 결과 | `ljm/tables/scoring_v2_5round_avg.json` |
| V2 보고서 | `ljm/tables/scoring_v2_report.md` |
| 역량 궤적 | `ljm/tables/capacity_trajectory.md` |
| ACW 데이터 | `ljm/data/acw_scoring.md` |
| 방법론 근거 | `ljm/data/method.md` |
