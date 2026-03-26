# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Korean academic paper on adaptive governance and policy design. Author: 이석민 (Lee Seogmin), 한신대학교.

**Single integrated paper**: SAPD 이론 + 6개 정부 실증 검증 → 한국행정학보 투고
- Title: 상태 기반 적응형 정책 설계(SAPD): AI 시대 정책 아키텍처
- Method: 개념적 분석 (Jaakkola 2020) + 다중 AI 스코어링 (5모델×5라운드)
- Current manuscript: `paper/drafts/paper_final_v6.md` (~28,000자 본문 + 33,500자 부록)
- Target: 본문 ≤27,000자 + 온라인 부록 (GitHub)

## Session Startup

Always read these files first:
1. `context.md` — project decisions, current state, expert panel rationale
2. `plan.md` — Phase A-E execution plan for editing v6
3. `paper/style/writing-style.md` — Korean academic writing conventions

## Key Decision (2026-03-26)

Originally planned as 2 separate papers, reversed to 1 integrated paper after expert panel review. Key reasons:
- 본문 ~28,000자 → 편집으로 27,000자 가능
- 이론-실증 선순환이 분리 시 파괴됨
- 한국 학계에서 순수 이론 논문 게재 어려움
- SAPD 이론이 정치적 민감성의 방어막 역할

## Language and Style

All outputs in **Korean (국문)**. Follow `paper/style/writing-style.md`:
- 격식체: ~이다, ~한다, ~된다
- 3인칭: "본 연구는"
- 과잉 수식 금지 (혁명적, 획기적 등)
- 인용: APA 7th Korean — (저자, 연도)
- 표: <표 1>, 그림: <그림 1>
- 본문 한도: 27,000자 원칙 (35,000자 상한)

## Repository Structure

```
president/
├── context.md, plan.md, research.md, CLAUDE.md
├── paper/                          # 논문 본체
│   ├── drafts/                     # 원고 + 부록 + 투고 자료
│   │   ├── paper_final_v6.md       # 현재 원본 (편집 대상)
│   │   ├── paper_final_v5.md       # 이전 버전
│   │   ├── appendices.md           # 부록 A-D 통합본
│   │   ├── appendix_A-D_*.md       # 개별 부록
│   │   ├── cover_letter*.md        # 커버레터
│   │   └── submission_checklist*.md
│   ├── review/phase7/              # 다중 LLM 리뷰 (3라운드)
│   ├── research/                   # Phase 1-5 연구 파이프라인 아카이브
│   └── style/writing-style.md      # 문체 가이드
└── data/                           # 실증 데이터 + 분석
    ├── analysis_main.md            # 단일 코더 5방법론 분석
    ├── full_report.md              # 다중 AI 스코어링 종합 보고서
    ├── scripts/                    # Python 스코어링 스크립트
    ├── raw/                        # 원시 데이터 (ACW, Policy Lag 등)
    └── tables/                     # 결과 JSON, 라운드별 데이터
```

## Critical Sensitivities

- **Political balance**: 이재명 정부 ACW 전 차원 1위 → 약점(Le3 협력적 리더십 결핍, 임기 초기 한계)을 반드시 부각
- **LLM methodology**: 한국 학계에서 전례 없음 → 정당화에 충분한 지면 필요
- **Human benchmark**: 인간 코더 벤치마크 부재 → 체계적 한계로 명시
- **Honeymon effect**: 임기 1년차 평가의 상향 편향 가능성 명시

## Python Scripts (data/scripts/)

No build system. Run individually: `python data/scripts/<script>.py`
- `ai_scoring_v2.py` — core scoring library (5 models, 2 panels)
- `multi_round_scoring.py` — 5-round repeated measurement
- `fix_*.py` — data cleaning scripts

## HWPX Conversion

Use the `hwp` skill for markdown → HWPX (한글) conversion for final submission.
