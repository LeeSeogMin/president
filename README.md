# 한국 역대 정부 적응적 거버넌스 역량 비교 연구

> **저자**: 이석민, 한신대학교 공공인재빅데이터융합학부
> **분석 기간**: 2003-2026 (노무현~이재명, 6개 정부)
> **논문**: 2편 (Paper A 실증 + Paper B SAPD 이론)

---

## 프로젝트 구조

```
president/
├── README.md                    # 이 파일
├── CLAUDE.md                    # AI 어시스턴트 지침
├── requirements.txt             # Python 의존성
│
├── paper/                       # 논문 본체
│   ├── paper_a_draft.md         # Paper A: 실증 비교 (현재 원고)
│   ├── paper_b_draft.md         # Paper B: SAPD 이론 (현재 원고)
│   ├── paper_a_outline.md       # Paper A 구조
│   ├── paper_b_outline.md       # Paper B 구조
│   ├── two_paper_structure.md   # 2논문 설계 문서
│   └── style/writing-style.md   # 한국어 학술 문체 가이드
│
├── data/
│   ├── verified/                # ★ 최종 검증 완료 데이터 (논문의 근거)
│   │   ├── tide_weighted.md     # T/I/D/E Hall 3차수 가중합
│   │   ├── agli_scoring_v2.md   # AGLI (Ostrom IAD, 0-4)
│   │   ├── lowi_strict_review.md # Lowi STRICT 적응적 도구 분류
��   │   ├── lowi_classification.md # Lowi 595 국정과제 전체 분류
│   ��   ├── lowi_validation.md   # Lowi 코딩 검증 (kappa=0.898)
│   │   ├── wgi_confidence.md    # WGI 추세제거 잔차 + 신뢰구간
│   │   ├── policy_lag_v2.md     # Policy Lag (OECD Agility, 20건)
│   │   ├── crisis_response_score.md # CRS (5 AI 블라인드 채점)
│   │   ├── composite_scoring.md # 종합 점수 (3방법 × 복수 가중치)
│   │   ├── adaptive_capacity_profile.md # 적응역량 프로파일 (비가산)
│   │   ├── tide_governor_ljm.md # 이재명 경기도지사 T/I/D/E
│   │   ├── panel2_ljm_local_gov.md # 이재명 지방정부 데이터
│   │   ├── ljm_leadership_analysis.md # 이재명 리더십 분석
│   │   ├── laws_summary.md      # 적응적 거버넌스 법률 요약
│   │   └── laws/                # 6개 핵심 법률 원문
│   │
│   ├── raw_downloads/           # 원시 데이터 (API, 스크래핑 등)
│   │   ├── wgi_full_dataset_2025.xlsx
│   │   ├── wgi_korea_*.json     # World Bank WGI API 응답
│   │   ├── oecd_dgi_full.csv    # OECD DGI 데이터
│   │   ├── crisis_timelines.md  # 20건 위기 사건일지
│   │   ├── blind_coding_responses.json # AI 블라인드 코딩 원시 응답
│   │   └── ...                  # 기타 원시 데이터
│   │
│   ├── scripts/                 # Python 분석 스크립트
│   │   ├── ai_scoring_v2.py     # 5모델 AI 스코어링 (ACW/제도)
│   │   ├── blind_coding.py      # T/I/D/E 블라인드 검증
│   ���   ├── crisis_scoring.py    # CRS 채점 (20건 × 5모델)
│   │   ├── action_evaluation.py # 행위 평가
│   │   └── multi_round_scoring.py # 다중 라운드 측정
│   │
│   └── raw_deprecated/          # 구버전·중간 산출물 (아카이브)
│       ├── archive_v1/          # 방법론 재설계 이전 파일
│       ├── intermediate/        # 중간 분석 파일
│       └── ...
```

## 5개 핵심 지표

| # | 지표 | 파일 | 방향 | 스케일 |
|---|------|------|:----:|--------|
| 1 | T/I/D/E 가중합 | `tide_weighted.md` | ↑ | Hall 3차수 가중 정수 |
| 2 | AGLI Flow | `agli_scoring_v2.md` | ↑ | Ostrom IAD 0-4, Delta |
| 3 | Lowi STRICT | `lowi_strict_review.md` | ↑ | 적응적 도구 채택률 (%) |
| 4 | WGI ���차 | `wgi_confidence.md` | ↑ | 추세제거 잔차 (탐색적) |
| 5 | CRS | `crisis_response_score.md` | ↑ | 위기 대응 적절성 0-4 |

## 확정 순위 (5개 정부, 10/10 시나리오 안정)

| 순위 | 정부 | 비고 |
|:---:|------|------|
| 1 | 문재인 | 모든 방법·가중치에서 1위 |
| 2 | 노무현 | |
| 3 | 이명박 | |
| 4 | 박근�� | |
| 5 | 윤석열 | |
| (잠정) | 이재명 | 0.8년 잠정치, 확정 비교 대상 아님 |

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

### 2. 필요 API 키

| 모델 | 환경 변수 | 발급처 |
|------|----------|--------|
| GPT-5.2 | `OPENAI_API_KEY` | [OpenAI](https://platform.openai.com) |
| Claude Sonnet 4.6 | `ANTHROPIC_API_KEY` | [Anthropic](https://console.anthropic.com) |
| Grok-4-1 | `XAI_API_KEY` | [xAI](https://console.x.ai) |
| Gemini 3 Flash | `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com) |
| HyperCLOVA HCX-007 | `CLOVA_STUDIO_API_KEY` | [NAVER Cloud](https://www.ncloud.com/product/aiService/clovaStudio) |

### 3. 분석 스크립트

```bash
# T/I/D/E 블라인드 검증
python data/scripts/blind_coding.py

# AI 행위 평가
python data/scripts/action_evaluation.py

# CRS 채점 (20건 위기 × 5모델)
python data/scripts/crisis_scoring.py
```

### 4. 주의사항

- LLM 응답 비결정성으로 결과가 소폭 변동될 수 있음 (temperature=0.3)
- 모델 버전 업데이트 시 결과 변동 가능. 원자료는 2026년 3월 기준
- GPT-5.2: `max_completion_tokens` 사용 필수
- HCX-007: 출력 토큰 한계로 배치 처리 필요

---

## 데이터 출��

| 데이터 | 출처 | 접근 |
|--------|------|------|
| WGI | [World Bank](https://info.worldbank.org/governance/wgi/) | REST API |
| OECD DGI | [OECD](https://www.oecd.org/governance/digital-government/) | SDMX API |
| UN EGDI | [UN DESA](https://publicadministration.un.org/egovkb/) | 웹사이트 |
| 법률 ���문 | [���가법령정보센터](https://www.law.go.kr) | 웹 스크래핑 |
| 국회 의안 | [열린���회정보](https://open.assembly.go.kr) | Open API |

---

## 라이선스

학�� 연구 목적. 인용 시 출처 명시.

```
이석민 (2026a). 한국 역대 정부 적응적 거버넌스 역량 비교: 체계적 탐색 분석.
이석민 (2026b). 상태 기반 적응형 정책 설계(SAPD): AI 시대 정책 아키텍처.
GitHub: https://github.com/LeeSeogMin/president
```
