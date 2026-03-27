# Blind T/I/D/E Validation Results

> 실행일: 2026-03-27 10:14:46
> 모델: GPT-5.2, Claude-Sonnet-4.6, Grok-4-1, Gemini-3-Flash, HCX-007
> 라운드: 3회
> Temperature: 0.2
> 검증 항목: 46개 경계 사례

## 1. 블라인드 레이블 매핑 (본 세션)

| 레이블 | 실제 정부 |
|--------|----------|
| 정부 Gamma | 노무현 |
| 정부 Epsilon | 이명박 |
| 정부 Beta | 박근혜 |
| 정부 Alpha | 문재인 |
| 정부 Delta | 윤석열 |
| 정부 Zeta | 이재명 |

## 2. 앵커링 비네트 결과

| 모델 | V1 (정답:T) | V2 (정답:I) | V3 (정답:D) | 정확도 | 신뢰 가중치 |
|------|:---:|:---:|:---:|:---:|:---:|
| GPT-5.2 | ✓ | ✓ | ✓ | 3/3 | 1.0 |
| Claude-Sonnet-4.6 | ✓ | ✓ | ✓ | 3/3 | 1.0 |
| Grok-4-1 | ✓ | ✓ | ✓ | 3/3 | 1.0 |
| Gemini-3-Flash | ✓ | ✓ | ✗(E) | 2/3 | 0.7 |
| HCX-007 | ✓ | ✓ | ✗(E) | 2/3 | 0.7 |

## 3. T/I/D/E 분류 일치도

### 3.1 연구자 vs 모델 일치율

| 모델 | 일치 항목 | 전체 | 일치율 | 가중 일치율 |
|------|:---:|:---:|:---:|:---:|
| GPT-5.2 | 31 | 46 | 67.4% | 67.4% |
| Claude-Sonnet-4.6 | 36 | 46 | 78.3% | 78.3% |
| Grok-4-1 | 37 | 46 | 80.4% | 80.4% |
| Gemini-3-Flash | 38 | 46 | 82.6% | 57.8% |
| HCX-007 | 5 | 6 | 83.3% | 58.3% |

### 3.2 Krippendorff's Alpha

- **모델 간 (5 AI models)**: α = 0.7294
- **연구자 포함 (연구자 + 5 models)**: α = 0.6868

## 4. 식별 테스트 (Identification Test)

기준 확률: 1/6 = 16.7% (무작위)

| 모델 | 정확 식별 | 전체 | 식별률 | 판정 |
|------|:---:|:---:|:---:|------|
| GPT-5.2 | 0 | 1 | 0.0% | 블라인딩 완전 성공 |
| Claude-Sonnet-4.6 | 0 | 1 | 0.0% | 블라인딩 완전 성공 |
| Grok-4-1 | 0 | 1 | 0.0% | 블라인딩 완전 성공 |
| Gemini-3-Flash | 0 | 1 | 0.0% | 블라인딩 완전 성공 |
| HCX-007 | 0 | 1 | 0.0% | 블라인딩 완전 성공 |

## 5. 항목별 상세 결과

| blind_id | original_id | 연구자 | GPT-5.2 | Claude-Sonnet-4.6 | Grok-4-1 | Gemini-3-Flash | HCX-007 |
|----------|-------------|:---:|:---:|:---:|:---:|:---:|:---:|
| B01 | 노무현-C1 | T+I | I | I | I | I | I |
| B02 | 노무현-C2 | I | I✓ | I✓ | I✓ | I✓ | I✓ |
| B03 | 노무현-C3 | T+I | T+I✓ | T+I✓ | T+I✓ | T+I✓ | T+I✓ |
| B04 | 노무현-E1 | I | I✓ | I✓ | I✓ | I✓ | I✓ |
| B05 | 이명박-A1 | I | T+I | T+I | I✓ | T+I | I✓ |
| B06 | 이명박-C1 | T+I- | D | I✓ | I-✓ | I✓ | I-✓ |
| B07 | 이명박-C2 | T | T✓ | T✓ | T✓ | T✓ | — |
| B08 | 이명박-C3 | T+I | T+I✓ | T+I✓ | T+I✓ | T+I✓ | — |
| B09 | 이명박-E1 | I | I✓ | I✓ | I✓ | I✓ | — |
| B10 | 이명박-F4 | I | I✓ | T+I | I✓ | I✓ | — |
| B11 | 박근혜-A2 | I (미완) | D | I✓ | I✓ | I+D✓ | — |
| B12 | 박근혜-C1 | I- | D | I✓ | D | I✓ | — |
| B13 | 박근혜-C2 | D | D✓ | D✓ | D✓ | D✓ | — |
| B14 | 박근혜-C3 | I- | D | I✓ | D | I✓ | — |
| B15 | 박근혜-E2 | T+I | T+I✓ | T+I✓ | T+I✓ | T+I✓ | — |
| B16 | 박근혜-F2 | I (미완) | D | I✓ | D | D | — |
| B17 | 박근혜-F3 | D | D✓ | D✓ | D✓ | D✓ | — |
| B18 | 문재인-A3 | I | T+I | T+I | I✓ | T+I | — |
| B19 | 문재인-C1 | T+I | I | I | I | I | — |
| B20 | 문재인-C2 | I | I✓ | I✓ | I✓ | I✓ | — |
| B21 | 문재인-C3 | T | T✓ | T✓ | T✓ | T✓ | — |
| B22 | 문재인-C4 | I | T+I | T+I | T+I | T+I | — |
| B23 | 문재인-E1 | I | I✓ | I✓ | I✓ | I✓ | — |
| B24 | 문재인-F1 | T+I | T+I✓ | T+I✓ | T+I✓ | T+I✓ | — |
| B25 | 문재인-F4 | I | I✓ | T+I | I✓ | I✓ | — |
| B26 | 윤석열-A1 | I | T+I | T+I | I✓ | I✓ | — |
| B27 | 윤석열-A2 | I | E | I✓ | I-✓ | I✓ | — |
| B28 | 윤석열-B1 | I | T | D | T | D | — |
| B29 | 윤석열-C1 | T | T✓ | T✓ | T✓ | T✓ | — |
| B30 | 윤석열-C2 | T | T✓ | T✓ | T✓ | T✓ | — |
| B31 | 윤석열-C3 | T | T✓ | T✓ | T✓ | T✓ | — |
| B32 | 윤석열-C4 | T+I | T+I✓ | T+I✓ | T+I✓ | T+I✓ | — |
| B33 | 윤석열-C5 | T | T✓ | T✓ | T✓ | T✓ | — |
| B34 | 윤석열-E1 | I | I✓ | I✓ | I✓ | I✓ | — |
| B35 | 윤석열-E2 | T+I | T+I✓ | T+I✓ | T+I✓ | T+I✓ | — |
| B36 | 윤석열-F1 | T+I | T+I✓ | T+I✓ | T+I✓ | T+I✓ | — |
| B37 | 윤석열-F4 | T | D | T+D✓ | D | D | — |
| B38 | 이재명-A1 | I | I✓ | I✓ | I✓ | I✓ | — |
| B39 | 이재명-A2 | I | I✓ | I✓ | I✓ | I✓ | — |
| B40 | 이재명-A3 | I | I✓ | I✓ | I✓ | I✓ | — |
| B41 | 이재명-A4 | T | T✓ | T✓ | T✓ | T✓ | — |
| B42 | 이재명-D1 | I | E | E | E | I+E✓ | — |
| B43 | 이재명-E1 | I | I✓ | I✓ | I✓ | I✓ | — |
| B44 | 이재명-E2 | T | T✓ | T✓ | T✓ | T✓ | — |
| B45 | 이재명-F1 | T+I | T+I✓ | T+I✓ | T+I✓ | T+I✓ | — |
| B46 | 이재명-F2 | T+I | T+I✓ | T+I✓ | T+I✓ | T+I✓ | — |

## 6. 불일치 항목 분석

### B01 (노무현-C1)
- 연구자: T+I
- GPT-5.2: I
- Claude-Sonnet-4.6: I
- Grok-4-1: I
- Gemini-3-Flash: I
- HCX-007: I

### B05 (이명박-A1)
- 연구자: I
- GPT-5.2: T
- Claude-Sonnet-4.6: T
- Gemini-3-Flash: T

### B06 (이명박-C1)
- 연구자: T+I-
- GPT-5.2: D

### B10 (이명박-F4)
- 연구자: I
- Claude-Sonnet-4.6: T

### B11 (박근혜-A2)
- 연구자: I (미완)
- GPT-5.2: D

### B12 (박근혜-C1)
- 연구자: I-
- GPT-5.2: D
- Grok-4-1: D

### B14 (박근혜-C3)
- 연구자: I-
- GPT-5.2: D
- Grok-4-1: D

### B16 (박근혜-F2)
- 연구자: I (미완)
- GPT-5.2: D
- Grok-4-1: D
- Gemini-3-Flash: D

### B18 (문재인-A3)
- 연구자: I
- GPT-5.2: T
- Claude-Sonnet-4.6: T
- Gemini-3-Flash: T

### B19 (문재인-C1)
- 연구자: T+I
- GPT-5.2: I
- Claude-Sonnet-4.6: I
- Grok-4-1: I
- Gemini-3-Flash: I

### B22 (문재인-C4)
- 연구자: I
- GPT-5.2: T
- Claude-Sonnet-4.6: T
- Grok-4-1: T
- Gemini-3-Flash: T

### B25 (문재인-F4)
- 연구자: I
- Claude-Sonnet-4.6: T

### B26 (윤석열-A1)
- 연구자: I
- GPT-5.2: T
- Claude-Sonnet-4.6: T

### B27 (윤석열-A2)
- 연구자: I
- GPT-5.2: E

### B28 (윤석열-B1)
- 연구자: I
- GPT-5.2: T
- Claude-Sonnet-4.6: D
- Grok-4-1: T
- Gemini-3-Flash: D

### B37 (윤석열-F4)
- 연구자: T
- GPT-5.2: D
- Grok-4-1: D
- Gemini-3-Flash: D

### B42 (이재명-D1)
- 연구자: I
- GPT-5.2: E
- Claude-Sonnet-4.6: E
- Grok-4-1: E

---

*Generated by blind_coding.py on 2026-03-27 10:14:46*