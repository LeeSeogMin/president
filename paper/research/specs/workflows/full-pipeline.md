# 이론 논문 작성 파이프라인 (10-Phase)

## 워크플로우 다이어그램

```
┌─────────────────┐
│  Phase 1        │  문헌 검토 & 이론적 포지셔닝
│  Literature     │  Output: literature_review.md, theoretical_positioning.md
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Phase 2        │  논증 설계
│  Argumentative  │  Output: argumentative_design.md, concept_definitions.md
│  Design         │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Phase 3        │  소스 자료 구축
│  Source Material │  Output: framework_taxonomy.md, paradigm_comparison.md
│  Construction   │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Phase 4        │  비교 프레임워크 분석
│  Comparative    │  Output: paradigm_analysis.md, isomorphism_analysis.md
│  Analysis       │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Phase 5        │  검증 & 논리적 정합성
│  Validation     │  Output: consistency_check.md, counter_arguments.md
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Phase 6        │  논문 초안 작성
│  Paper Drafting │  Output: paper_draft_v1.md (~20,000자)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Phase 7        │  다중 LLM 리뷰
│  Multi-LLM      │  Output: paper_draft_final.md
│  Review         │  (반복 최대 3회)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Phase 8        │  AI 탐지 & 인간화
│  AI Detection   │  Output: humanized_paper.md
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Phase 9        │  전문 편집
│  Editing        │  Output: paper_edited.md
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Phase 10       │  투고 패키지
│  Submission     │  Output: paper_final.md, paper_final.docx
└─────────────────┘
```

## Phase별 완료 기준

| Phase | 완료 기준 |
|-------|----------|
| 1 | 40+ 문헌 검토, 5+ 연구 갭, 이론적 포지셔닝 문서 완성 |
| 2 | P1-P4 명제 확정, 분석 전략 확정, 핵심 개념 정의 완성 |
| 3 | 프레임워크 분류표, EBP vs SBAP 비교표, 팔란티어 사례 정리 |
| 4 | 패러다임 비교 분석, SAPD 차별화 분석, 동형성 분석 완성 |
| 5 | 내부 정합성, 경계 조건, 반론 대응 문서 완성 |
| 6 | 논문 초안 ~20,000자, 참고문헌 40-60편 |
| 7 | 3회 이상 리뷰 반영, 최종 드래프트 확정 |
| 8 | AI 탐지율 감소 확인 |
| 9 | 문법/스타일/일관성 교정 완료 |
| 10 | 최종 MD + DOCX + 커버레터 패키지 |
