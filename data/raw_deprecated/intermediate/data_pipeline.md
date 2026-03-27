# 한국 정부 데이터 수집 파이프라인 설계서

> 작성일: 2026-03-26
> 목적: 대통령별 정부 효과성 비교 논문을 위한 데이터 수집 자동화

---

## 0. 긴급 발견: 기존 데이터 오류

### 파이프라인 테스트 과정에서 발견된 기존 `intl_indices.md` 데이터와 실제 소스 간의 불일치:

| 지표 | 항목 | 기존 데이터 | 실제 소스 값 | 차이 |
|------|------|-----------|------------|------|
| **WGI** | 2023년 추정치 | +1.16 | **+1.405** | 0.245 차이 |
| **WGI** | 2022년 추정치 | +1.25 | **+1.349** | 0.099 차이 |
| **WGI** | 2003년 추정치 | +1.00 | **+0.790** | 0.210 차이 |
| **OECD DGI** | 2023년 종합 | 0.64 (3위) | **0.935 (1위)** | 완전히 다른 값 |
| **OECD DGI** | 6개 차원 전체 | 0.50~0.72 | **0.882~1.000** | 전 차원 불일치 |

**추가 검증 -- 백분위(Percentile Rank) 비교:**

| 연도 | 기존 백분위 | 실제 API 백분위 | 기존 추정치 | 실제 API 추정치 |
|------|-----------|---------------|-----------|---------------|
| 2003 | 80.5 | **76.22** | +1.00 | **+0.790** |
| 2008 | 86.4 | **79.61** | +1.27 | **+0.994** |
| 2013 | 83.0 | **79.62** | +1.14 | **+1.003** |
| 2017 | 82.2 | **80.95** | +1.10 | **+1.029** |
| 2022 | 85.6 | **90.09** | +1.25 | **+1.349** |
| 2023 | 83.5 | **90.57** | +1.16 | **+1.405** |

**원인 분석**: 기존 데이터는 추정치와 백분위가 **모두** 실제 API 값과 불일치. WGI 데이터가 시간에 따라 소급 개정(retroactive revision)되므로, 과거 특정 시점의 스냅샷과 현재 최신 데이터가 다를 수 있음. 또는 출처 오류. DGI는 2019 pilot 값을 2023에도 적용한 것으로 보임 (실제 2023 DGI는 완전히 새로운 방법론, 한국 1위).

**조치 필요**: 아래 파이프라인으로 전체 재검증 및 교정 필수. WGI는 "최신 API 기준" vs "해당 연도 원본 보고서 기준" 중 어느 것을 사용할지 결정 필요.

---

## 1. World Bank WGI (정부 효과성)

### 접근 방법: REST API (직접 호출, 인증 불필요)

**상태: 검증 완료 -- 즉시 사용 가능**

### API 엔드포인트

```
https://api.worldbank.org/v2/country/KOR/indicator/GE.EST?format=json&date=2000:2025
```

### 주요 파라미터
| 파라미터 | 값 | 설명 |
|---------|-----|------|
| `country` | KOR | 한국 |
| `indicator` | GE.EST | Government Effectiveness: Estimate |
| `indicator` | GE.PER.RNK | Government Effectiveness: Percentile Rank |
| `format` | json | 응답 형식 (xml도 가능) |
| `date` | 2000:2025 | 기간 범위 |

### 추가 지표 (동일 API 구조)
- `RQ.EST` - Regulatory Quality
- `RL.EST` - Rule of Law
- `VA.EST` - Voice and Accountability
- `CC.EST` - Control of Corruption
- `PS.EST` - Political Stability

### 실제 수신 데이터 (2023년 기준)
```
KOR | 2023 | GE.EST = 1.405
KOR | 2022 | GE.EST = 1.349
KOR | 2021 | GE.EST = 1.366
...
KOR | 2000 | GE.EST = 0.614
```

### 추천 도구: **Python requests** (가장 간단)
### 구현 스크립트

```python
import requests
import json
import csv

INDICATORS = {
    "GE.EST": "Government_Effectiveness_Estimate",
    "GE.PER.RNK": "Government_Effectiveness_Percentile",
    "RQ.EST": "Regulatory_Quality_Estimate",
    "RL.EST": "Rule_of_Law_Estimate",
    "CC.EST": "Control_of_Corruption_Estimate",
}

BASE_URL = "https://api.worldbank.org/v2/country/KOR/indicator/{indicator}?format=json&date=2000:2025&per_page=100"

all_data = []
for code, name in INDICATORS.items():
    url = BASE_URL.format(indicator=code)
    resp = requests.get(url)
    data = resp.json()
    if len(data) > 1:
        for entry in data[1]:
            if entry["value"] is not None:
                all_data.append({
                    "indicator": name,
                    "year": entry["date"],
                    "value": round(entry["value"], 3),
                })

# CSV 저장
with open("wgi_korea.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["indicator", "year", "value"])
    writer.writeheader()
    writer.writerows(all_data)
```

---

## 2. UN EGDI (전자정부 발전지수)

### 접근 방법: World Bank Data360 API 또는 UN 사이트 Excel 다운로드

**상태: 검증 완료 -- 두 가지 경로 사용 가능**

### 경로 A: World Bank Data360 API (추천)
```
https://data360api.worldbank.org/data360/data?dataset=UN_EGDI&country=KOR
```

### 경로 B: UN 공식 사이트 직접 다운로드
- URL: `https://publicadministration.un.org/egovkb/en-us/data-center`
- "Download 2024 Data in Excel/CSV format" 링크 제공
- JavaScript 렌더링 필요하여 **firecrawl** 또는 **Chrome 자동화** 권장

### 경로 C: 수동 확인용 (직접 페이지)
- 한국 프로파일: `https://publicadministration.un.org/egovkb/en-us/Data/Country-Information/id/90-Republic-of-Korea`

### 추천 도구: **Python requests** (Data360 API) 또는 **firecrawl** (UN 사이트)

### 구현 스크립트

```python
import requests

# Data360 API 경로
url = "https://data360api.worldbank.org/data360/data"
params = {
    "dataset": "UN_EGDI",
    "country": "KOR",
}
resp = requests.get(url, params=params)
data = resp.json()
# 연도별 EGDI 점수, OSI, TII, HCI 하위지수 포함
```

---

## 3. OECD DGI (디지털정부지수)

### 접근 방법: PDF 추출 + OECD SDMX API

**상태: PDF에서 정확한 데이터 추출 완료**

### 핵심 발견
- 기존 데이터 파일의 2023 DGI 수치가 **완전히 잘못됨**
- 실제 2023 DGI에서 한국은 **1위 (종합 0.935)**

### 실제 2023 DGI 한국 점수 (PDF Annex A에서 추출)

| 차원 | 한국 점수 | OECD 평균 | 순위 |
|------|----------|-----------|------|
| Digital by Design | 0.971 | 0.684 | 상위 |
| Data-Driven Public Sector | **1.000** | 0.633 | **1위** |
| Government as a Platform | 0.913 | 0.615 | 상위 |
| Open by Default | 0.882 | 0.525 | 상위 |
| User-Driven | 0.909 | 0.607 | 상위 |
| Proactiveness | 0.934 | 0.567 | 상위 |
| **종합 (Composite)** | **0.935** | **0.605** | **1위** |

### 데이터 접근 경로

#### 경로 A: OECD SDMX API (프로그래밍)
```
https://sdmx.oecd.org/public/rest/data/OECD.GOV.DIGO,DSD_DGI@DF_DGI,1.0/KOR...
```
- OECD SDMX API 기반 (인증 불필요, 무료)
- 문서: https://www.oecd.org/en/data/insights/data-explainers/2024/09/api.html

#### 경로 B: PDF 직접 파싱 (검증 완료)
```
PDF URL: https://www.oecd.org/content/dam/oecd/en/publications/reports/2024/01/2023-oecd-digital-government-index_b11e8e8e/1a89ed5e-en.pdf
```
- firecrawl의 PDF 파서로 테이블 추출 성공
- Annex A (p.25)에 전체 국가별 점수 포함

#### 경로 C: 시각화 페이지
```
https://goingdigital.oecd.org/en/indicator/58
```
- JavaScript 렌더링 필요 → Chrome 자동화 또는 firecrawl actions 필요

### 추천 도구: **firecrawl PDF 파서** (가장 신뢰성 높음)

### 구현

```python
# firecrawl MCP를 사용한 PDF 추출 (이미 테스트 완료)
# mcp__firecrawl__firecrawl_scrape 호출:
#   url: PDF URL
#   formats: ["markdown"]
#   parsers: ["pdf"]
#   pdfOptions: {"maxPages": 30}
# → Annex A 테이블에서 KOR 행 파싱

# 또는 OECD SDMX API:
import requests
url = "https://sdmx.oecd.org/public/rest/data/OECD.GOV.DIGO,DSD_DGI@DF_DGI,1.0/KOR...."
headers = {"Accept": "application/vnd.sdmx.data+json"}
resp = requests.get(url, headers=headers)
```

---

## 4. 법제처 국가법령정보센터 (law.go.kr)

### 접근 방법: firecrawl 스크래핑 (검증 완료) + Open API (등록 필요)

**상태: firecrawl로 즉시 사용 가능, Open API는 IP 등록 필요**

### 경로 A: firecrawl 스크래핑 (즉시 사용 가능, 검증 완료)

```
URL 패턴: https://www.law.go.kr/법령/{법령명}
```

**테스트 완료 결과:**

| 법령 | 법률 번호 | 공포일 | 시행일 |
|------|----------|--------|--------|
| 인공지능 발전과 신뢰 기반 조성 등에 관한 기본법 | 법률 제21311호 | 2026.1.20 | 2026.1.22 |
| 규제자유특구 및 지역특화발전특구에 관한 규제특례법 | 법률 제21381호 | 2026.2.19 | 2026.7.1 |
| 정부업무평가 기본법 | 법률 제21065호 | 2025.10.1 | 2026.1.2 |

### firecrawl 구현 (JSON 모드)

```json
{
  "url": "https://www.law.go.kr/법령/인공지능기본법",
  "formats": ["json"],
  "jsonOptions": {
    "prompt": "Extract law name, law number, promulgation date, enforcement date, enacting body, and key provisions",
    "schema": {
      "type": "object",
      "properties": {
        "law_name": {"type": "string"},
        "law_number": {"type": "string"},
        "promulgation_date": {"type": "string"},
        "enforcement_date": {"type": "string"},
        "enacting_body": {"type": "string"},
        "key_provisions": {"type": "array", "items": {"type": "string"}}
      }
    }
  },
  "waitFor": 5000
}
```

### 경로 B: Open API (서버 IP 등록 필요)

```
신청 사이트: https://open.law.go.kr/LSO/main.do
API URL: http://www.law.go.kr/DRF/lawSearch.do?OC={인증키}&target=law&type=XML&query={검색어}
```

**주의**: Open API 사용 시 서버 IP와 도메인을 사전 등록해야 함. 로컬 환경에서는 인증 실패 확인됨.

### 추천 도구: **firecrawl** (등록 불필요, JSON 추출 정확도 높음)

---

## 5. 국회 의안정보시스템 (likms.assembly.go.kr)

### 접근 방법: 국회 Open API (data.go.kr 경유)

**상태: API 경로 확인됨, 서비스키 발급 필요**

### 직접 스크래핑 문제
- `likms.assembly.go.kr/bill/billDetail.do?billId=...` 접속 시 메인 페이지로 리다이렉트됨
- JavaScript SPA 구조로 firecrawl 일반 스크래핑 실패
- **Chrome 자동화(mcp__claude-in-chrome)** 또는 **Open API** 필요

### Open API 경로 (추천)

#### 공공데이터포털 API
```
포털: https://www.data.go.kr/data/15126134/openapi.do
API 서비스: 국회사무처_의안정보 통합 API
엔드포인트: https://open.assembly.go.kr/portal/data/service/selectAPIServicePage.do/OOWY4R001216HX11440
```

#### 열린국회정보 직접 API
```
포털: https://open.assembly.go.kr/portal/openapi/openApiNaListPage.do
```

### 필요 파라미터
| 파라미터 | 설명 |
|---------|------|
| KEY | 인증키 (공공데이터포털에서 발급) |
| Type | xml 또는 json |
| pIndex | 페이지 번호 (기본 1) |
| pSize | 페이지당 건수 (기본 100) |
| BILL_NAME | 의안명 검색 |

### 구현 스크립트

```python
import requests

API_KEY = "발급받은_서비스키"
BASE_URL = "https://open.assembly.go.kr/portal/openapi/의안정보API"

# AI 기본법 관련 의안 검색
params = {
    "KEY": API_KEY,
    "Type": "json",
    "pIndex": 1,
    "pSize": 100,
    "BILL_NAME": "인공지능",
}
resp = requests.get(BASE_URL, params=params)
bills = resp.json()
```

### 대안: Chrome 자동화 (서비스키 없이)

```
도구: mcp__claude-in-chrome__navigate
URL: https://likms.assembly.go.kr/bill/main.do
→ 검색창에 법안명 입력
→ mcp__claude-in-chrome__get_page_text 로 결과 추출
```

### 추천 도구: **Open API** (정확성) > **Chrome 자동화** (유연성)

---

## 6. 정책브리핑 (korea.kr)

### 접근 방법: firecrawl 검색 + 공공데이터포털 API

**상태: firecrawl 검색으로 즉시 사용 가능**

### 경로 A: firecrawl 검색 (즉시 사용 가능, 검증 완료)

```json
{
  "query": "site:korea.kr \"인공지능 기본법\" 보도자료",
  "limit": 10
}
```

**테스트 결과 (AI기본법 관련):**
- 2026.01.22: 「인공지능기본법」 시행 보도자료
- 2026.01.23: 인공지능기본법 시행 관련 추가 설명
- 2026.03.26: AI기본법 제도개선 연구반 출범

### 경로 B: 공공데이터포털 보도자료 API

```
API: 문화체육관광부_정책브리핑_보도자료_API
포털: https://www.data.go.kr/data/15095295/openapi.do
```

### 경로 C: 직접 보도자료 페이지 스크래핑

```
보도자료 목록: https://www.korea.kr/briefing/pressReleaseList.do
개별 보도자료: https://www.korea.kr/briefing/pressReleaseView.do?newsId={newsId}
```

### 추천 도구: **firecrawl search** (가장 빠름) > **공공데이터포털 API** (체계적)

---

## 7. 통합 파이프라인 실행 계획

### 즉시 실행 가능 (인증 불필요)

| 순서 | 데이터 | 도구 | 소요시간 |
|------|--------|------|---------|
| 1 | WGI 전체 시계열 | Python requests | 1분 |
| 2 | OECD DGI 점수표 | firecrawl PDF 파싱 | 2분 |
| 3 | 법제처 법령 정보 | firecrawl JSON 스크래핑 | 법령당 30초 |
| 4 | 정책브리핑 보도자료 | firecrawl search | 검색당 10초 |

### 사전 등록 필요

| 순서 | 데이터 | 필요 조치 | 예상 소요 |
|------|--------|----------|----------|
| 5 | UN EGDI 시계열 | Data360 API 테스트 또는 UN 사이트 다운로드 | 즉시~1일 |
| 6 | 국회 의안정보 | data.go.kr 서비스키 발급 | 1~3일 |
| 7 | 법제처 Open API | open.law.go.kr IP 등록 | 1~3일 |

### 우선 조치 사항

1. **긴급**: `intl_indices.md`의 WGI 및 OECD DGI 데이터를 API/PDF 원본으로 교정
2. **금일**: WGI API로 전체 시계열 재다운로드, DGI PDF에서 정확한 점수 반영
3. **이번주**: data.go.kr에서 국회 의안정보 API 서비스키 신청
4. **계속**: firecrawl로 법령·보도자료 수시 수집

---

## 8. 도구별 적합성 요약

| 데이터 소스 | firecrawl | WebFetch | Chrome 자동화 | Python API | 최적 선택 |
|------------|-----------|----------|-------------|-----------|----------|
| World Bank WGI | - | O | - | **최적** | Python requests |
| UN EGDI | O (JS사이트) | X (렌더링실패) | O | O (Data360) | Python + Data360 |
| OECD DGI | **최적** (PDF) | X (403) | O | O (SDMX) | firecrawl PDF |
| 법제처 법령 | **최적** | X (JS필요) | O | X (IP등록필요) | firecrawl JSON |
| 국회 의안정보 | X (리다이렉트) | X | O | **최적** (API등록후) | Open API |
| 정책브리핑 | **최적** | O | O | O (API등록후) | firecrawl search |
