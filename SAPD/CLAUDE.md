# CLAUDE.md - Agent Layer Memory

> 이 파일은 Claude Code가 프로젝트 컨텍스트를 유지하기 위한 메모리 파일입니다.

## 프로젝트 개요

**프로젝트 이름**: State-based Adaptive Policy 이론 논문
**논문 제목(가제)**: "상태 기반 적응형 정책: 증거 기반 정책을 넘어선 실시간 정책 설계 프레임워크"
**목적**: 상태 기반 적응형 정책(State-based Adaptive Policy) 패러다임과 SAPD Framework의 이론적 기초를 확립하는 학술 논문 작성
**현재 Phase**: Phase 1 시작 전 (인프라 구축 중)
**논문 유형**: 이론/개념적 논문 (Theoretical/Conceptual Paper)

### 외부 메모리 컨텍스트 관리

> **세션 시작 시 반드시 `context.md`와 `todo.md`를 먼저 읽을 것.**

| 파일 | 용도 | 저장 시점 |
|------|------|----------|
| **`context.md`** | 현재 진행 상황, 완료 작업, 의사결정 기록 | Phase/단계 완료, 의사결정, 세션 종료 전 |
| **`todo.md`** | 할 일, 블로커, 다음 단계 | 위와 동일 + 장시간 작업(30분+) 중간 체크포인트 |

**논문 언어**: **국문 (Korean)** — 국내 학술지 투고용
**작업 언어**: **한글 (Korean)** — 모든 작업 및 산출물 한글로 진행
**프레임워크 약어**: **SAPD** (State-based Adaptive Policy Design)
**타겟 저널**: 한국행정학보, 한국정책학회보, 정보화정책 등 국내 학술지

### 분량 가이드라인

| 항목 | 기준 |
|------|------|
| **본문 글자 수** | 약 20,000자 (참고문헌·도표·부록 제외) |
| **초록 (Abstract)** | 국문 300자 + 영문 150 words |
| **키워드** | 국문 5개 + 영문 5개 |

## 연구 질문

> **증거 기반 정책(Evidence-based Policy)의 구조적 한계를 극복하는 새로운 정책 패러다임으로서, '상태 기반 적응형 정책(State-based Adaptive Policy)'은 어떤 이론적 기초와 설계 아키텍처를 통해 실시간 적응형 거버넌스를 구현할 수 있는가?**

### 핵심 명제 (Propositions)

**P1**: 증거 기반 정책은 시간 지연(Time Lag) 문제로 인해 동태적 환경에서 구조적으로 불충분하다.

**P2**: 정책 시스템은 상태 전이 함수 `Decision(t) = f(State(t)) → State(t+1)`로 모델링 가능하며, 이는 연속적 피드백 루프를 통해 적응력을 확보한다.

**P3**: SAPD Framework의 5단계 아키텍처(문제구조화 → 전략구조화 → 의사결정아키텍처 → 데이터통합 → 평가/피드백)는 상태 기반 적응형 정책을 구현하기 위한 충분한 설계 명세를 제공한다.

**P4**: SAPD 아키텍처는 민간 영역의 실시간 의사결정 플랫폼(팔란티어)과 구조적 동형성(Structural Isomorphism)을 나타내며, 이는 적응형 정책의 보편적 설계 원리의 존재를 시사한다.

## SAPD Framework 정의

### 5-Layer 아키텍처
1. **L1. 문제 구조화 (Problem Structuring)**: 시스템 경계와 정책 문제 정의
2. **L2. 전략 구조화 (Strategy Structuring)**: 전략적 구조와 성과 논리 정의
3. **L3. 의사결정 아키텍처 (Decision Architecture)**: 의사결정 노드, 권한, 기준 정의
4. **L4. 데이터 통합 (Data Integration)**: 데이터와 AI를 시스템에 통합
5. **L5. 평가 및 적응형 피드백 (Evaluation & Adaptive Feedback)**: 지속적 평가 및 적응 메커니즘

### 핵심 공식
```
State(t) → Decision(t) = f(State(t)) → System Response → State(t+1) → [반복]
```

## 재활용 콘텐츠

| 파일 | 경로 | 활용 |
|------|------|------|
| objective.md | `c:/Dev/my-life/objective.md` | SAPD 정의, 5-Layer, AI 역할 |
| intro.mdx | `c:/Dev/my-life/content/writing/intro.mdx` | Time Lag 논증, EBP 한계 |
| sapd-palantir-convergence.mdx | `c:/Dev/my-life/content/writing/sapd-palantir-convergence.mdx` | 팔란티어 구조적 동형성 |

## Phase 진행 상태

| Phase | 이름 | 상태 |
|-------|------|------|
| 1 | 문헌 검토 & 이론적 포지셔닝 | ⬜ 대기 |
| 2 | 논증 설계 | ⬜ 대기 |
| 3 | 소스 자료 구축 | ⬜ 대기 |
| 4 | 비교 프레임워크 분석 | ⬜ 대기 |
| 5 | 검증 & 논리적 정합성 | ⬜ 대기 |
| 6 | 논문 초안 작성 | ⬜ 대기 |
| 7 | 다중 LLM 리뷰 | ⬜ 대기 |
| 8 | AI 탐지 & 인간화 | ⬜ 대기 |
| 9 | 전문 편집 | ⬜ 대기 |
| 10 | 투고 패키지 | ⬜ 대기 |
