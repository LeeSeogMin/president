# 한국 역대 정부 적응적 거버넌스 역량 비교 연구

> **저자**: 이석민, 한신대학교 공공인재빅데이터융합학부
> **분석 기간**: 2003-2026 (노무현~이재명, 6개 정부)

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

#### 블라인드 T/I/D/E 검증
```bash
python data/scripts/blind_coding.py
```
- 입력: `data/verified/tide_attribution.md`
- 출력: `data/verified/blind_validation_results.md`
- 원자료: `data/raw_downloads/blind_coding_responses.json`

#### AI 행위 평가
```bash
python data/scripts/action_evaluation.py
```
- 입력: `data/verified/tide_attribution.md`
- 출력: `data/verified/action_evaluation_results.md`
- 원자료: `data/raw_downloads/action_evaluation_raw.json`

### 4. 주의사항

- LLM 응답 비결정성으로 결과가 소폭 변동될 수 있음 (temperature=0.2)
- 모델 버전 업데이트 시 결과 변동 가능. 원자료는 2026년 3월 기준
- GPT-5.2: `max_completion_tokens` 사용 필수
- HCX-007: 출력 토큰 한계로 배치 처리 필요 (6건/배치)

---

## 데이터 출처

| 데이터 | 출처 | 접근 |
|--------|------|------|
| WGI | [World Bank](https://info.worldbank.org/governance/wgi/) | REST API |
| OECD DGI | [OECD](https://www.oecd.org/governance/digital-government/) | SDMX API |
| UN EGDI | [UN DESA](https://publicadministration.un.org/egovkb/) | 웹사이트 |
| 법률 원문 | [국가법령정보센터](https://www.law.go.kr) | 웹 스크래핑 |
| 국회 의안 | [열린국회정보](https://open.assembly.go.kr) | Open API |

---

## 라이선스

학술 연구 목적. 인용 시 출처 명시.

```
이석민 (2026). 한국 역대 정부 적응적 거버넌스 역량 비교 연구.
GitHub: https://github.com/LeeSeogMin/president
```
