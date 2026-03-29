# 분석 방법론 상세 문서

> **작성일**: 2026-03-29 (개정)
> **이전 버전**: data/raw_deprecated/method_v1_20260302.md
> **정본**: paper/paper_a_draft.md 3장과 일관
> **목적**: 본 연구에서 사용하는 5개 독립 지표 + 1개 파생 프로파일의 원전, 조작적 정의, 코딩 방식, AI 스코어링 구조를 상세히 기술

---

## 방법론 변경 이력: Old → New

### 변경 배경

2026-03-26 이론-조작화 감사(`data/raw_deprecated/intermediate/indicator_theory_audit.md`)에서 기존 방법론(method_old.md, 2026-03-02)에 HIGH 심각도 문제 3건이 발견되었다.

| # | 문제 | 기존 방법론 | 심각도 | 근거 문서 |
|---|------|-----------|:------:|----------|
| 1 | **ACW 순환 의존** | ACW 점수를 WGI/INST/Lowi/TIDE에서 파생하여, 독립 지표가 아닌 합성물이 됨 | HIGH | indicator_theory_audit.md §1 "Circular Dependency Problem" |
| 2 | **법 존재 = 학습 오류** | INST(Argyris 기반)를 법률 존재 여부로 채점. Argyris의 핵심 통찰(espoused theory vs theory-in-use 괴리)을 무시 | HIGH | indicator_theory_audit.md §3 "Law Existence = Learning Fallacy" |
| 3 | **질적 유형론의 정량화 범주 오류** | Streeck-Thelen의 과정적 제도 변화 유형론을 건수 집계(Net=I-I--D)로 변환. 원 이론이 의도하지 않은 산술 연산 | HIGH | indicator_theory_audit.md §2 "Category Error" |

### 전문가 패널 권고 (2026-03-27)

편향 제거 전문가 패널(`data/raw_deprecated/expert_reports/05_bias_removal_panel.md`)이 **Option E (3층 하이브리드)** 만장일치 권고:
- 제1층: Action Inventory — 점수 이전에 사실을 확정
- 제2층: T/I/D/E Attribution — 추세(T)와 외부 충격(E) 분리로 축적 편향 통제
- 제3층: Blind AI Validation — AI를 평가자가 아닌 검증자로 재배치

### 지표별 변경 내역

| Old (method_old.md) | 문제 | New (현재) | 해결 |
|---------------------|------|-----------|------|
| 방법 A: ACW = 독립 지표 | 순환 의존 | ACW = **파생 프로파일** (독립 지표에서 격하), "not additive" 준수 | 순환 의존 인정 |
| 방법 B: Policy Lag = 인지 지연 일수 | 속도만 측정, 질적 적절성 미반영 | **지표 4: CRS** (3차원: 인지+적절성+집행) | 다차원 확장 |
| 방법 C: WGI+EGDI+DGI 3개 국제지표 | 중복, 귀속 불가 | **지표 5: WGI만** (추세제거 잔차, 탐색적 보조) | EGDI/DGI 제거 |
| 방법 D: INST (Argyris 0-2) | 법 존재=학습 오류 | **지표 2: AGLI** (Ostrom IAD 0-4, rules-in-form/use 구분) | 이론적 기반 변경 |
| 방법 E: Lowi 키워드 기반 | 산업 육성 키워드 오분류 | **지표 3: Lowi STRICT** (Broad vs STRICT 이중 기준) | 엄격 필터 도입 |
| 없음 | 축적 편향 미통제 | **지표 1: T/I/D/E** + Hall 3차수 가중합 | T/E 제외로 축적 편향 통제 |
| AI가 전 지표 직접 평가 | 정치적 편향 우려 | AI 역할 이원화 (직접 스코어링 + 보조 검증) | 지표별 적합 역할 배정 |

### 방법론 개선 (2026-03-28~29)

방법론 타당성 검토(`data/raw_deprecated/internal_reviews/review_methodology_synthesis.md`)와 내부 전문가 패널 평가를 거쳐 추가 개선:

| 이슈 | 개선 내용 |
|------|----------|
| M9: Fleiss kappa 척도 불일치 | Krippendorff's alpha(ordinal) 병행 산출 |
| M11: temperature 비일관 | 전 스크립트 0.2 통일 |
| M12: 이재명 컨텍스트 비대칭 | 6개 정부 동등 팩트시트 주입 |
| M14: CRS 블라인딩 수준 | Level 1 → Level 2 (대통령명+정당명+고유사건명+연도) |
| H2: 블라인딩 실효성 미검증 | 식별 테스트(identification test) 추가 |

---

## 개요: 코딩 방식의 이원 구조

본 연구의 코딩·채점은 지표의 성격에 따라 두 가지 방식으로 수행된다.

| 방식 | 해당 지표 | 1차 수행자 | AI 역할 |
|------|----------|:---------:|--------|
| 연구자 코딩 + AI 보조 검증 | T/I/D/E (지표 1), Lowi STRICT (지표 3) | 연구자 1인 | 경계 사례 Level 2 블라인드 교차 검토 |
| AI 직접 스코어링 | ACW (프로파일), AGLI (지표 2), CRS (지표 4) | 5개 LLM | 독립 코더로 직접 채점, 3라운드 반복 |
| 공개 데이터 | WGI (지표 5) | — | 대상 아님 |

### 5개 LLM 독립 코더

| 모델 | 제공사 | 특성 |
|------|--------|------|
| GPT-5.2 | OpenAI | 영어 중심 범용 모델 |
| Claude Sonnet 4.6 | Anthropic | 영어 중심 범용 모델 |
| Grok-4-1 | xAI | 영어 중심, 실시간 데이터 접근 |
| Gemini 3 Flash | Google | 다국어, 장문 처리 |
| HyperCLOVA HCX-007 | NAVER | 한국어 특화 모델 |

### 공통 설정
- temperature: **0.2** (전 스크립트 통일)
- 반복 측정: **3라운드** 평균
- 팩트시트: 6개 정부에 **동등한 배경 정보** 주입 (data/gov_factsheets.md)
- 신뢰도: **Krippendorff's alpha(ordinal)** 주 지표, Fleiss' kappa(명목) 보조

### 편향 통제
- Level 2 블라인딩: 대통령명·정당명·고유사건명·연도 치환
- 동등 팩트시트: 정부별 ~500자 배경 정보 동일 구조로 주입 (M12 해결)
- 인간 코더 벤치마크 부재: LLM 간 일치도(inter-AI agreement)가 인간 전문가와의 일치를 보장하지 않음 → 구조적 한계, 후속 검증 필요

---

## 지표 1: T/I/D/E Hall 3차수 가중합

### 원전

- **Hall, P.A. (1993)**. "Policy Paradigms, Social Learning, and the State: The Case of Economic Policymaking in Britain." *Comparative Politics*, 25(3), 275-296.
  - 정책 변동의 3차수 구분: 1차수(설정값 조정), 2차수(도구 교체), 3차수(패러다임 전환)
- **Pierson, P. (2004)**. *Politics in Time*. Princeton University Press.
  - 경로의존(path dependence)과 증가수익(increasing returns) 메커니즘
- **Streeck, W. & Thelen, K. (2005)**. *Beyond Continuity*. Oxford University Press.
  - 점진적 제도 변화 5유형: 중층화(layering), 표류(drift), 전환(conversion), 대체(displacement), 소진(exhaustion)
- **Sabatier, P.A. (1988)**. "An Advocacy Coalition Framework of Policy Change."
  - 외부 충격과 정책학습의 상호작용

### T/I/D/E 분류 체계

| 코드 | 정의 | 조작적 기준 | 비교 포함 |
|------|------|------------|:--------:|
| T | 시대적 추세(Trend) | 전임 입법 승계, 글로벌 추세 동조 | 제외 |
| I | 의도적 행위(Intentional) | 새 입법, 조직 개편, 위기 대응의 명확한 의사결정 | 포함 |
| I- | 의도적 부정(Intentional Negative) | 명시적 정책 결정(폐지, 거부권, 예산 삭감 등)이 문서로 확인된 경우 | 포함 |
| D | 표류(Drift) | 법·조직이 유지되나 집행 지연·조정 실패·대응 부재가 관찰된 경우 | 포함 |
| E | 외부 충격(External) | 글로벌 위기, 기술 패러다임 전환 | 제외 |

**코딩 규칙**:
- T와 E를 비교 대상에서 제외하여 축적 편향과 외부 충격의 영향을 통제
- T+I 혼합 코드: I 성분에만 가중치를 부여, 혼합 사실은 별도 표기
- **결과지표(WGI, EGDI 등)의 변동은 코딩 대상에서 제외**, 외부 준거로만 활용
- I-와 D 판정: 결과지표 하락만으로는 편입하지 않음

### Hall 3차수 가중치

| 차수 | 정의 | 가중치 | 예시 |
|:----:|------|:------:|------|
| 1차수 | 설정값 조정 | 1 | 예산 규모 조정, 기존 제도 미세 수정 |
| 2차수 | 도구 교체 | 2 | 새 법률 제정, 새 조직 설치 |
| 3차수 | 패러다임 전환 | 3 | 헌정 질서 변동, 근본적 체제 전환 |

가중합 = Σ(I_k × k) - Σ(I⁻_k × k) - Σ(D_k × k) (k = 1, 2, 3)

**민감도 분석**: 1/2/3 외에 1/3/5(고차수 강화), 1/1/1(단순 건수)을 적용. 상위 4개 정부 순위 동일, 하위 그룹에서만 1/1/1 시 역전 확인 → 강건성 확인됨.

### 검증
- 연구자 1인이 1차 코딩 → 5개 LLM이 경계 사례(borderline=Y)를 Level 2 블라인드 교차 검토
- 블라인드: 정부명·날짜·법률명 제거, 그리스 문자(Alpha~Zeta)로 무작위 치환
- 행위 방향성 Krippendorff's alpha ≈ 0.73 (acceptable)
- 스크립트: `data/scripts/blind_coding.py`
- 원시 응답: `data/raw_downloads/blind_coding_responses.json`
- 결과: `data/verified/tide_weighted.md`

---

## 지표 2: AGLI (적응적 거버넌스 법제도 지표)

### 원전

- **Ostrom, E. (2005)**. *Understanding Institutional Diversity*. Princeton University Press.
  - IAD(Institutional Analysis and Development) 프레임워크
  - **rules-in-form**(공식 법규) vs **rules-in-use**(실제 운영 규범)의 구분
- **Dietz, T., Ostrom, E., & Stern, P.C. (2003)**. "The Struggle to Govern the Commons." *Science*, 302(5652), 1907-1912.
  - 다층적 제도, 분석적 심의, 제도 적합성(institutional fit)

### 설계

AGLI는 Ostrom IAD의 rules-in-form/rules-in-use 구분을 **제한적으로 차용**하여 법제도 운영 수준을 측정하는 0-4 척도 지표이다. IAD의 행위 상황(action arena), 결과 변수 등은 차용 범위에 포함되지 않는다.

**4개 차원**:

| 차원 | 내용 | 0점 | 4점 |
|------|------|-----|-----|
| D1 정책 피드백 | 정책 결과를 체계적으로 환류하는 공식 제도 | 제도 부재 | 체계적 운영 + 환류 |
| D2 정책 실험 | 소규모 실험→확대의 제도적 경로 | 제도 부재 | 체계적 실험 + 본허가 전환 |
| D3 시민참여 | 시민의 정책 피드백을 수집·반영하는 채널 | 기본 채널만 | 체계적 참여 + 법적 환류 |
| D4 AI/디지털 | AI·디지털 기술 기반 정책 의사결정 구조 | 제도 부재 | 전담 기구 + 차등 규제 |

**Stock vs Flow**:
- Stock: 특정 시점의 법제도 환경 총량 (합계/16)
- Flow(Delta): 전임 정부 대비 변동분 → **비교에서 사용**되는 값
- 축적 편향을 통제하기 위해 Flow를 채택

### 스코어링
- 5개 LLM이 독립 코더로 직접 채점 (AI 직접 스코어링 방식)
- 3라운드 반복 측정 평균
- 코더 간 신뢰도: Krippendorff's alpha(ordinal) = 0.689~0.712 (acceptable)
- Fleiss' kappa(명목) = 0.363~0.368 (fair) — 명목 척도에서는 낮으나, 서열 척도에 적합한 alpha로는 수용 가능
- 스크립트: `data/scripts/ai_scoring_v2.py --panel 1` (INST 분석)
- 원시 점수: `data/scripts/tables/scoring_v2_raw.json`
- 결과: `data/verified/agli_scoring_v2.md`

---

## 지표 3: Lowi STRICT 적응적 도구 비율

### 원전

- **Lowi, T.J. (1964)**. "American Business, Public Policy, Case-Studies, and Political Theory." *World Politics*, 16(4), 677-715.
- **Lowi, T.J. (1972)**. "Four Systems of Policy, Politics, and Choice." *Public Administration Review*, 32(4), 298-310.
  - 4유형: 배분(distributive), 규제(regulatory), 재분배(redistributive), 구성(constituent)
- **Schneider, A. & Ingram, H. (1990)**. "Behavioral Assumptions of Policy Tools." *Journal of Politics*, 52(2), 510-529.
  - 정책 도구 5유형: 권위, 유인, 역량 구축, 상징·권고, 학습
- **Gupta, J. et al. (2010)**. ACW 프레임워크의 적응적 거버넌스 정의

### 설계

6개 정부의 전체 595개 국정과제를 Lowi 4유형으로 분류한 후, **STRICT 기준**으로 적응적 도구 포함 여부를 판정.

**개념 정의**:
Lowi STRICT 적응적 도구는 정책 내용 일반이 아니라, **거버넌스 설계 자체에 학습·실험·환류 메커니즘이 내장된 정책 수단**을 뜻한다. 핵심은 특정 정책이 AI, 디지털, 혁신을 표방하는가가 아니라, 정책 집행 과정에서 상태 변화나 피드백을 반영하여 수정·조정될 수 있도록 설계되어 있는가에 있다. 따라서 산업 육성, 투자 확대, 인프라 확충처럼 결과 목표만 제시하는 과제는 Broad 기준에서는 적응적으로 읽힐 수 있어도 STRICT 기준에서는 제외된다.

**STRICT 기준** (Broad 기준과 구분):

| 유형 | 정의 | 핵심 판별 |
|------|------|----------|
| 실험적(Experimental) | 시범사업, 파일럿, 테스트베드 | 정책을 전면 시행 전 테스트하는가? |
| 샌드박스(Sandbox) | 규제 유예 기반 혁신 실험 | 규제를 유예하여 실험 공간을 만드는가? |
| 데이터 기반 의사결정 | 데이터·AI를 거버넌스 설계 자체에 활용 | 의사결정에 데이터 피드백이 내장되어 있는가? |
| 반복적 수정 | 단계적, 점진적, 재검토, 갱신 | 피드백에 따라 수정·갱신되도록 설계되었는가? |

**핵심 구분**: "AI·디지털 산업 육성(배분정책)" ≠ 적응적 거버넌스 도구

### 구체적 사례

STRICT 기준에서 최종 확정된 사례는 595건 중 4건이다.

| 정부 | 과제명 | 적응적 유형 | 판정 근거 |
|------|--------|-------------|----------|
| 박근혜 | 국민 중심 서비스 정부 3.0 구현 | 데이터 기반 의사결정 | 행정서비스 운영에 데이터 활용과 환류 체계를 직접 결합 |
| 윤석열 | 디지털플랫폼정부 구현 | 데이터 기반 의사결정 | 정부 운영 전반에 데이터 통합과 피드백 구조를 내장 |
| 이재명 | AI 민주정부 실현 | 데이터 기반 의사결정 | AI·데이터를 행정 의사결정 체계 자체에 결합 |
| 이재명 | 신산업 규제 재설계 | 샌드박스 | 규제 유예와 실증을 통해 결과를 다시 제도 설계에 반영 |

반대로 다음과 같은 과제는 STRICT에서 제외된다.

- AI·디지털 산업 육성 정책: 기술 투자나 산업 진흥이 중심일 뿐, 거버넌스 설계에 학습·환류 장치가 내장되지 않은 경우
- 일반 인프라 확충 과제: 디지털 인프라를 확대하더라도 상태 전환이나 피드백 반영 구조가 없는 경우
- 수사적 혁신 과제: "스마트", "혁신", "디지털" 같은 표현이 있으나 정책 수정 메커니즘이 없는 경우

### 검증
- Lowi 4유형 분류: 연구자 1인 코딩
- 타당성 검증: 무작위 추출 40개 과제 재분류, **Cohen's kappa = 0.898** (Almost Perfect Agreement)
- STRICT 판정: 연구자 1인 + 탈락 사유 체계적 기록
- 결과: Broad 32건(5.4%) → STRICT **4건(0.7%)**
- **변별력 한계**: STRICT 4건으로 정부 간 변별력 제한적. 이 지표 단독으로 적응적 거버넌스 역량 차이를 입증하기 어려우며, 발견 자체("한국 국정과제의 적응적 도구 내장이 극히 희소")가 핵심 기여
- 결과: `data/verified/lowi_strict_review.md`, `data/verified/lowi_classification.md`

---

## 지표 4: CRS (위기 대응 적절성 점수)

### 원전

- **Friedman, M. (1960)**. *A Program for Monetary Stability*. Fordham University Press.
  - 내부 시차(inside lag)와 외부 시차(outside lag) 개념
- **Argyris, C. & Schon, D.A. (1978)**. *Organizational Learning*.
  - 이중순환학습(double-loop learning): 위기 이후 제도적 학습
- **OECD (2021)**. *Government at a Glance 2021: Government Agility*.
  - 민첩한 정책(agile policy): 선제적, 적시적, 반응적

### 설계

3차원 × 0-4 척도:

| 차원 | 내용 | Friedman 대응 |
|------|------|:------------:|
| D1 인지·결정 신속성 | 위기 인지~실질적 결정까지의 속도 | inside lag |
| D2 대응 적절성 | 위기 유형에 적합한 정책 대응 | — |
| D3 집행 실효성 | 결정된 정책의 실제 집행 효과 | outside lag |

**사례 선정 기준**:
1. 사회적 충격 규모 (사망자 수, 경제 피해, 헌정 질서 영향)
2. 유형 다양화 (자연재해·감염병·경제·안보·정치 중 2개 이상)
3. 정부의 공식 대응이 문서화된 사례

정부당 3-4건, 총 20건 (19건 채점, 1건 진행 중 제외)

### 블라인딩 (Level 2)
- 대통령명·정당명: 그리스 문자(Alpha~Zeta)로 치환
- 고유사건명: 일반화 ("세월호"→"여객선 침몰 사고", "코로나19"→"감염병 대유행" 등)
- 연도: "YYYY"로 치환
- 정부 식별 억제를 위한 역추론 테스트(identification test) 내장

### 스코어링
- 5개 LLM이 블라인드 사례를 독립 채점
- 산출: 3차원 합계 / 3 → 사례별 5모델 평균 → 정부별 사례 평균
- 스크립트: `data/scripts/crisis_scoring.py`
- 원시 채점: `data/raw_deprecated/crisis_scoring_results.json`
- 결과: `data/verified/crisis_response_score.md`

### 한계
- LLM의 사전 학습 데이터에 사후적 여론·언론 평가가 포함되어 있어, 사후 평가 편향(hindsight bias)이 채점에 반영되었을 가능성
- 다만 5개 이질적 모델의 합의는 단일 모델 편향보다 강건하며, 사후적 합의가 기존 전문가 평가와 대체로 일치

---

## 지표 5: WGI 추세제거 잔차 (탐색적)

### 원전

- **Kaufmann, D., Kraay, A., & Mastruzzi, M. (2010)**. "The Worldwide Governance Indicators: Methodology and Analytical Issues." *World Bank Policy Research Working Paper* No. 5430.
  - 200개국, 6개 차원, 35개 교차 소스
  - 주관적 인식(perceptions) 기반 가중 합성 지표
  - 모든 점수에 표준오차(SE) 동반

### 설계
- **Government Effectiveness** 차원만 활용
- 2000-2023년 시계열에 선형 추세(기울기 +0.026/년, R²=0.73)를 적합
- **추세제거 잔차(detrended residual)** 산출
- 탐색적 보조 지표로만 활용 — 인과적 차이 입증 증거로 해석하지 않음

### 통계적 한계
- SE ~ 0.20이 임기 간 잔차 차이(최대 0.39)와 동일 규모
- 95% 신뢰구간에서 모든 대통령의 잔차가 0을 포함
- 대통령 간 잔차 차이 통계적으로 비유의 (p > 0.33)

### 데이터 출처
- World Bank REST API: `data/raw_downloads/wgi_korea_GE_EST.json`
- 원시 데이터셋: `data/raw_downloads/wgi_full_dataset_2025.xlsx`
- 결과: `data/verified/wgi_confidence.md`

---

## 파생 프로파일: 적응역량 프로파일 (ACW 6차원)

### 원전

- **Gupta, J. et al. (2010)**. ACW 프레임워크
  - 6차원 22기준: 다양성(V), 학습 역량(Lc), 자율적 변화(RAC), 리더십(Le), 자원(Re), 공정 거버넌스(FG)
  - **"not additive"** 경고: 차원 간 합산은 부적절

### 설계
- 5개 독립 지표의 결과를 ACW 6차원에 매핑
- 종합 총점 순위 미산출, 프로파일 패턴 비교에 한정
- 총점 대신 **Borda(순위 합계)를 탐색적 참고값**으로 제시

### 범주화 기준
- 해당 차원의 기준 중 양수(+1 이상) 비율:
  - 100% = 강점, 75%+ = 양호, 50%+ = 혼재, 25%+ = 중립, 미만 = 약점

### 스코어링
- 5개 LLM이 ACW 22기준(-2~+2)을 직접 채점
- 3라운드 반복 측정 평균
- 코더 간 신뢰도: alpha(ordinal) = 0.689~0.712
- 스크립트: `data/scripts/ai_scoring_v2.py --panel 1` (ACW 분석)
- 원시 점수: `data/scripts/tables/scoring_v2_raw.json`
- 3라운드 평균: `data/scripts/tables/scoring_v2_5round_avg.json`
- 결과: `data/verified/adaptive_capacity_profile.md`

---

## Panel 2: 이재명 지방정부 (성남시장·경기도지사)

### 설계
- Panel 1(중앙정부 6개 대통령)과 **별도 패널**로 구성
- 직접 점수 비교가 아닌 **패턴 관찰용**

### 기능적 등가성(functional equivalence)
- 중앙정부 법률·대통령령 ↔ 지방정부 조례·규칙
- 적용 불가 기준은 제외 (성남: 19/22, 경기: 20/22)

### 스코어링
- 동일한 5개 LLM + 동일 temperature(0.2) + 동일 라운드(3)
- 스크립트: `data/scripts/ai_scoring_v2.py --panel 2`
- 결과: `data/verified/panel2_ljm_local_gov.md`, `data/verified/tide_governor_ljm.md`, `data/verified/ljm_leadership_analysis.md`

---

## 지표 간 상관 및 한계

### T/I/D/E ↔ AGLI 상관
- Spearman ρ = 0.883 (p = 0.020, N=6)
- 동일 정책 행위(법률 제정 등)가 양쪽에 반영 → 구성적 중복 존재
- Borda 해석 시 이중 반영 가능성에 유의

### Lowi STRICT 변별력
- 595건 중 4건(0.7%)만 통과, 3개 정부가 0건
- 변별력 제한적이나, "한국 국정과제의 적응적 도구 내장이 극히 희소"라는 발견 자체가 핵심 기여

### 구조적 한계
1. **인간 코더 벤치마크 부재**: LLM 간 일치도 ≠ 인간과의 일치 → 향후 과제
2. **사후 평가 편향**: LLM의 학습 데이터에 사후적 정보 포함 → 구조적 한계
3. **N=6**: 통계적 추론 불허, 질적 비교 사례 연구로 해석
4. **이재명 0.8년**: 잠정 평가, 확정적 순위 비교에서 제외

---

## 데이터 파일 매핑

| 지표 | 원본 데이터 | 스크립트 | 출력 | 결과 |
|------|-----------|---------|------|------|
| T/I/D/E | 연구자 코딩 (부록 A) | blind_coding.py | blind_coding_responses.json | tide_weighted.md |
| AGLI | laws/ (6건) | ai_scoring_v2.py (INST) | scoring_v2_raw.json | agli_scoring_v2.md |
| Lowi | lowi_classification.md | — (수동) | — | lowi_strict_review.md |
| CRS | crisis_timelines.md | crisis_scoring.py | crisis_scoring_results.json | crisis_response_score.md |
| WGI | wgi_*.json, xlsx | — (통계 분석) | — | wgi_confidence.md |
| ACW | — | ai_scoring_v2.py (ACW) | scoring_v2_raw.json | adaptive_capacity_profile.md |
| Panel 2 | panel2_ljm_local_gov.md | ai_scoring_v2.py --panel 2 | scoring_v2_raw.json | ljm_leadership_analysis.md |

---

## 참고문헌

- Argyris, C. & Schon, D.A. (1978). *Organizational Learning*. Addison-Wesley.
- Cohen, J. (1960). "A Coefficient of Agreement for Nominal Scales." *Educational and Psychological Measurement*, 20(1), 37-46.
- Dietz, T., Ostrom, E., & Stern, P.C. (2003). "The Struggle to Govern the Commons." *Science*, 302(5652), 1907-1912.
- Friedman, M. (1960). *A Program for Monetary Stability*. Fordham University Press.
- Gupta, J. et al. (2010). "The Adaptive Capacity Wheel." *Environmental Science & Policy*, 13(6), 459-471.
- Grothmann, T. et al. (2013). "Assessing institutional capacities to adapt to climate change." *NHESS*, 13, 3369-3384.
- Hall, P.A. (1993). "Policy Paradigms, Social Learning, and the State." *Comparative Politics*, 25(3), 275-296.
- Kaufmann, D., Kraay, A., & Mastruzzi, M. (2010). "The Worldwide Governance Indicators." *World Bank WP* No. 5430.
- Lowi, T.J. (1972). "Four Systems of Policy, Politics, and Choice." *PAR*, 32(4), 298-310.
- OECD (2021). *Government at a Glance 2021: Government Agility*.
- Ostrom, E. (2005). *Understanding Institutional Diversity*. Princeton University Press.
- Pahl-Wostl, C. (2009). "Adaptive capacity and multi-level learning." *GEC*, 19(3), 354-365.
- Pierson, P. (2004). *Politics in Time*. Princeton University Press.
- Sabatier, P.A. (1988). "An Advocacy Coalition Framework." *Policy Sciences*, 21(2-3), 129-168.
- Schneider, A. & Ingram, H. (1990). "Behavioral Assumptions of Policy Tools." *Journal of Politics*, 52(2), 510-529.
- Streeck, W. & Thelen, K. (2005). *Beyond Continuity*. Oxford University Press.
