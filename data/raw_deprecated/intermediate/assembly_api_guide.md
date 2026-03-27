# 국회 의안정보 API 가이드

작성일: 2026-03-26

---

## 1. 개요: 두 가지 경로

국회 의안정보를 API로 수집하는 경로는 두 가지이다.

| 구분 | 공공데이터포털 (data.go.kr) | 열린국회정보 (open.assembly.go.kr) |
|------|---------------------------|----------------------------------|
| 역할 | 메타데이터 연계 포털 (LINK 유형) | **실제 API 제공 서버 (원천)** |
| 인증키 | data.go.kr 자체 키 (이 API에서는 불필요) | open.assembly.go.kr 자체 인증키 필요 |
| 핵심 | data.go.kr 페이지에서 "바로가기" 클릭 시 열린국회정보로 이동 | 직접 API 호출 가능 |

**결론: 실제 API 호출은 모두 `open.assembly.go.kr`에서 이루어진다. data.go.kr의 해당 API는 "LINK" 유형으로, 열린국회정보 포털로 연결만 해줄 뿐이다.**

---

## 2. 공공데이터포털 (data.go.kr) 정보

### 서비스 페이지
- URL: https://www.data.go.kr/data/15126134/openapi.do
- 서비스명: **국회 국회사무처_의안정보 통합 API**
- 제공기관: 국회 국회사무처
- 관리부서: 기획조정실 디지털운영담당관실
- 전화번호: **02-6788-3056**
- API 유형: **LINK** (자체 호스팅이 아닌 외부 링크)
- 데이터포맷: XML (JSON도 지원)
- 비용: 무료
- 업데이트 주기: 실시간
- 활용신청 수: 732건
- 이용허락범위: 제한 없음
- 바로가기: https://open.assembly.go.kr/portal/data/service/selectAPIServicePage.do/OOWY4R001216HX11440

### 중요 공지 (2026-01-20)
기존 구 API 3종이 **폐기 예정**이며, 대체 API로 전환됨:
- ~~국회 국회사무처_의안 정보~~ (data.go.kr/data/3037286) --> **의안정보 통합 API** (15126134)로 대체
- ~~국회 국회사무처_의원 정보~~ --> 국회의원 정보 통합 API로 대체
- ~~국회 국회사무처_의사일정 정보~~ --> 국회일정 통합 API로 대체

### data.go.kr에서의 활용신청 방법
이 API는 LINK 유형이므로, data.go.kr에서 별도 서비스키를 발급받을 필요가 없다.
바로가기 링크를 통해 열린국회정보 포털에서 직접 인증키를 발급받아 사용한다.

---

## 3. 열린국회정보 (open.assembly.go.kr) - 원천 API

### 3-1. 인증키 발급 절차

**발급 방식: 회원가입 후 온라인 신청 (즉시 또는 단기 승인)**

1. **회원가입/로그인**: https://open.assembly.go.kr 접속 후 회원가입 및 로그인
2. **인증키 신청 페이지 이동**:
   - 상단 메뉴 "오픈API" 탭 클릭
   - 또는 마이페이지 > "인증키 발급"
   - 직접 URL: https://open.assembly.go.kr/portal/openapi/openApiActKeyPage.do?tabIdx=1
3. **활용목적 작성**: 인증키 활용 목적과 내용 기재
4. **인증키 발급 신청 버튼 클릭**
5. **발급 확인**: 마이페이지 > "인증키 발급내역"에서 확인
   - 사용 여부가 "정상"인지 확인

**참고사항:**
- 인증키 1개로 열린국회정보 포털의 **모든 Open API**에서 공통 사용 가능
- 인증키는 타인에게 공유하지 말 것 (호출량 공유 문제)
- 인증키가 틀리면 API 응답을 받을 수 없음

### 3-2. 의안정보 통합 API (ALLBILL) 상세

#### 엔드포인트
```
https://open.assembly.go.kr/portal/openapi/ALLBILL
```

#### 필수 파라미터 (기본인자)

| 파라미터 | 타입 | 필수 | 설명 | 기본값 |
|----------|------|------|------|--------|
| KEY | STRING | Y | 인증키 | sample (테스트용) |
| Type | STRING | Y | 응답포맷 (xml 또는 json) | xml |
| pIndex | INT | Y | 페이지 번호 | 1 |
| pSize | INT | Y | 페이지당 건수 | 100 (sample키는 5로 고정) |

#### 요청인자 (선택/검색 조건)
- **BILL_NO**: 의안번호 (필수인자로 사용됨)
- 기타 선택 인자는 API 상세 페이지에서 확인

#### 샘플 요청 URL
```
https://open.assembly.go.kr/portal/openapi/ALLBILL?KEY=sample&Type=json&pIndex=1&pSize=5&BILL_NO=2211084
```

#### 응답 포맷
XML 또는 JSON (Type 파라미터로 지정)

### 3-3. 의안 관련 주요 API 목록 (엔드포인트 경로)

연구 목적에 따라 다양한 API를 조합하여 사용할 수 있다.

#### 핵심 API

| API명 | 엔드포인트 경로 | 필수인자 | 용도 |
|--------|----------------|----------|------|
| 의안정보 통합 | `ALLBILL` | 의안번호(BILL_NO) | 의안 종합정보 (link 포함) |
| 국회의원 발의법률안 | `nzmimeepazxkubdpn` | 대수(AGE) | 의원발의 법률안 목록 |
| 의안별 표결현황 | `ncocpgfiaoituanbr` | 대수(AGE) | 찬/반/기권/총 투표수 |
| 의안검색 | `TVBPMBILL11` | 없음 | 전체 의안 검색 (11만건+) |

#### 의안 상세정보 API

| API명 | 엔드포인트 경로 | 필수인자 | 용도 |
|--------|----------------|----------|------|
| 의안 상세정보 | `BILLINFODETAIL` | 의안ID | 의안 상세 |
| 의안 제안자정보 | `BILLINFOPPSR` | 의안ID | 제안자 목록 |
| 의안 접수목록 | `BILLRCP` | 대수(AGE) | 접수된 의안 목록 |
| 의안 심사정보 | `BILLJUDGE` | 대수(AGE) | 심사 진행상황 |
| 위원회심사 회의정보 | `BILLJUDGECONF` | 의안ID | 위원회 심사 회의 |
| 법사위 회의정보 | `BILLLWJUDGECONF` | 의안ID | 법사위 심사 회의 |

#### 법률안 심사 및 처리 API

| API명 | 엔드포인트 경로 | 필수인자 | 용도 |
|--------|----------------|----------|------|
| 계류의안 | `nwbqublzajtcqpdae` | 없음 | 현재 계류 중인 의안 |
| 처리의안 | `nzpltgfqabtcpsmai` | 대수 | 처리 완료 의안 |
| 최근 본회의처리 의안 | `nxjuyqnxadtotdrbw` | 대수 | 최근 본회의 처리 건 |
| 본회의부의안건 | `nayjnliqaexiioauy` | 없음 | 본회의 상정 안건 |

#### 처리 의안통계 API

| API명 | 엔드포인트 경로 | 필수인자 |
|--------|----------------|----------|
| 총괄 | `BILLCNTMAIN` | 대수 |
| 발의주체별 법률안 | `BILLCNTPRPSR` | 대수 |
| 위원회별 법률안 | `BILLCNTLAWCMIT` | 대수 |
| 위원회별 | `BILLCNTCMIT` | 대수 |
| 의안종류별/위원회별 | `BILLCNTLAWDIV` | 대수 |

#### 본회의 처리안건 API

| API명 | 엔드포인트 경로 | 필수인자 |
|--------|----------------|----------|
| 법률안 | `nkalemivaqmoibxro` | 대수 |
| 예산안 | `nbslryaradshbpbpm` | 대수 |
| 결산 | `nwbpacrgavhjryiph` | 대수 |
| 기타 | `nzgjnvnraowulzqwl` | 대수 |

### 3-4. API 호출 공통 패턴

모든 API의 호출 URL 형식:
```
https://open.assembly.go.kr/portal/openapi/{엔드포인트경로}?KEY={인증키}&Type={xml|json}&pIndex={페이지번호}&pSize={페이지크기}&{추가파라미터}
```

예시:
```bash
# 22대 국회 의원발의 법률안 조회 (JSON)
curl "https://open.assembly.go.kr/portal/openapi/nzmimeepazxkubdpn?KEY=YOUR_KEY&Type=json&pIndex=1&pSize=100&AGE=22"

# 의안정보 통합 API (특정 의안번호)
curl "https://open.assembly.go.kr/portal/openapi/ALLBILL?KEY=YOUR_KEY&Type=json&pIndex=1&pSize=5&BILL_NO=2211084"

# 전체 API 목록 조회
curl "https://open.assembly.go.kr/portal/openapi/OPENSRVAPI?KEY=YOUR_KEY&Type=json&pIndex=1&pSize=300"
```

---

## 4. 인증키 발급 구체적 절차 (사용자 newmind69 기준)

### 방법 A: 열린국회정보에서 직접 발급 (권장)

1. **브라우저에서 접속**: https://open.assembly.go.kr
2. **회원가입** (아직 미가입 시):
   - 열린국회정보는 data.go.kr과 별도 계정 체계
   - 별도 회원가입 필요
3. **로그인 후 인증키 신청**:
   - 상단 메뉴 > 오픈API > 마이페이지 > 인증키 발급
   - 또는 직접 URL: https://open.assembly.go.kr/portal/openapi/openApiActKeyPage.do?tabIdx=1
4. **활용목적 기재**: "학술연구 - 국회 의안 분석" 등
5. **발급 신청 버튼 클릭**
6. **인증키 확인**: 마이페이지 > 인증키 발급내역

### 방법 B: 공공데이터포털 경유

1. https://www.data.go.kr 로그인 (ID: newmind69)
2. https://www.data.go.kr/data/15126134/openapi.do 페이지 이동
3. "바로가기" 버튼 클릭 --> 열린국회정보로 이동
4. 이후 방법 A의 2~6단계 동일

**참고**: data.go.kr의 API 유형이 "LINK"이므로 data.go.kr 자체에서 서비스키를 발급받는 것이 아니라, 열린국회정보 포털에서 직접 인증키를 발급받아야 한다.

---

## 5. 주요 출력 필드 참고 (의안정보 통합 API 기준)

- `BILL_NO`: 의안번호
- `BILL_NAME`: 의안명
- `PROPOSER`: 제안자 (예: "홍길동의원 등 11인")
- `RST_PROPOSER`: 대표발의자 (예: "홍길동")
- `PUBL_PROPOSER`: 공동발의자 목록 (콤마 구분)
- `PROPOSE_DT`: 제안일
- `PROC_RESULT`: 처리 결과
- `LINK_URL`: 의안 상세 페이지 링크
- `COMMITTEE`: 소관위원회

---

## 6. 참고 문서 및 링크

- 공공데이터포털 API 페이지: https://www.data.go.kr/data/15126134/openapi.do
- 열린국회정보 메인: https://open.assembly.go.kr/portal/openapi/main.do
- 열린국회정보 인증키 신청: https://open.assembly.go.kr/portal/openapi/openApiActKeyPage.do?tabIdx=1
- 전체 API 목록 API: https://open.assembly.go.kr/portal/openapi/OPENSRVAPI
- 참고 블로그 (의안 API 분석): https://velog.io/@assembly101/OpenAPI-의안-관련-사용-참고-문서-작성-진행중
- 참고 영상 (사용법): https://www.youtube.com/watch?v=kmN9w3PUhxU
- 관리부서 전화: 02-6788-3056 (국회사무처 디지털운영담당관실)
- 담당자: 남규태 주무관 (2026-01 공지 기준)
