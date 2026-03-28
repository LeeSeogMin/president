# Crisis Response Score (위기 대응 적절성 점수)

> 작성일: 2026-03-28
> 방법: 18개 위기 사례 × 5 AI 모델 블라인드 채점 (D1 인지·결정 + D2 적절성 + D3 집행, 각 0-4)
> 최종 점수: 3차원 합계 / 3 → 사례별 모델 평균 → 정부별 사례 평균
> 스케일: 0-4 (높을수록 좋음)

---

## 정부별 Crisis Response Score

| 정부 | 사례 1 | 사례 2 | 사례 3 | **CRS** |
|------|--------|--------|--------|:-------:|
| 노무현 | Case 1 | Case 2 | Case 3 | **3.53** |
| 이명박 | Case 4 | Case 5 | Case 6 | **3.4** |
| 박근혜 | Case 7 | Case 8 | Case 9 | **2.07** |
| 문재인 | Case 10 | Case 11 | Case 12 | **3.76** |
| 윤석열 | Case 13 | Case 14 | Case 15 | **2.04** |
| 이재명 | Case 16 | Case 17 | Case 18 | **3.09** |

---

## Composite Scoring 반영

- 기존 Recognition Lag를 **Crisis Response Score**로 교체
- 방향: 높을수록 좋음
- 스케일: 0-4

---

*5개 AI 모델의 블라인드 독립 채점을 통해 산출. 채점 원시 데이터는 raw_deprecated/crisis_scoring_results.md 참조.*