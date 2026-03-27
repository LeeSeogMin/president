# 원자료 다운로드 목록 (Raw Downloads)

> 다운로드일: 2026-03-27
> 목적: 모든 API 원시 응답을 보존하여 재현 가능성 확보

---

## World Bank WGI (정부 효과성 + 추가 지표)

| 파일 | 지표 | API URL |
|------|------|---------|
| `wgi_korea_GE_EST.json` | Government Effectiveness: Estimate | `api.worldbank.org/v2/country/KOR/indicator/GE.EST?format=json&date=2000:2025` |
| `wgi_korea_GE_PERCENTILE.json` | Government Effectiveness: Percentile | `api.worldbank.org/v2/country/KOR/indicator/GE.PER.RNK?format=json&date=2000:2025` |
| `wgi_korea_RQ_EST.json` | Regulatory Quality | `api.worldbank.org/v2/country/KOR/indicator/RQ.EST?format=json&date=2000:2025` |
| `wgi_korea_RL_EST.json` | Rule of Law | `api.worldbank.org/v2/country/KOR/indicator/RL.EST?format=json&date=2000:2025` |
| `wgi_korea_VA_EST.json` | Voice and Accountability | `api.worldbank.org/v2/country/KOR/indicator/VA.EST?format=json&date=2000:2025` |
| `wgi_korea_CC_EST.json` | Control of Corruption | `api.worldbank.org/v2/country/KOR/indicator/CC.EST?format=json&date=2000:2025` |
| `wgi_oecd_38_GE_EST.json` | OECD 38개국 GE Estimate (DiD 대조군) | 38개국 코드 일괄 조회 |
| `wgi_full_dataset_2025.xlsx` | 전체 WGI 데이터셋 (1996-2024, 전 세계) | `datacatalogfiles.worldbank.org/.../wgidataset_with_sourcedata-2025.xlsx` |

## OECD DGI (디지털정부지수)

| 파일 | 내용 | API URL |
|------|------|---------|
| `oecd_dgi_full.csv` | 전체 DGI 데이터 (438행, 전 국가) | `sdmx.oecd.org/public/rest/v2/data/dataflow/OECD.GOV.GIP/DSD_GOV@DF_GOV_DGOGD_2025/1.0/` |

## 노무현 정부 원본 문서

| 파일 | 내용 | 출처 |
|------|------|------|
| `roh_policy_tasks_2003.pdf` | 참여정부 국정비전과 국정과제 (2003.2.21) | 97imf.kr/items/show/3738 |

## 국회의안 (열린국회정보 API)

국회의안 API는 curl/Python 직접 접근 시 400 Bad Request 발생 (WebFetch 도구로만 성공).
원자료는 `data/verified/assembly_bills.md`에 API 응답 내용 그대로 기록됨.
- 검색어: 인공지능 (21대, 22대), 이태원 (21대)
- API 엔드포인트: `open.assembly.go.kr/portal/openapi/nzmimeepazxkubdpn`
- 인증키: 발급 완료 (파일 미저장)

## UN EGDI

UN EGOVKB 사이트는 프로그래밍 방식 접근 차단. 브라우저에서 수동 수집.
원자료는 `data/verified/un_egdi_korea.md`에 UN 공식 사이트 데이터 그대로 기록됨.
- 출처: publicadministration.un.org/egovkb/en-us/Data/Country-Information/id/138-Republic-of-Korea

## 법률 원문 (국가법령정보센터)

firecrawl로 스크래핑한 6개 법률 원문은 `data/verified/laws/` 폴더에 개별 파일로 저장됨.
- 출처: law.go.kr
