
# Ticker Map (ticker-map)
국내외 주식 티커 메타데이터 및 사용자 정의 별칭(Alias)을 통합 관리하고, 퀀트/자동매매 시스템에서 즉각적으로 쿼리할 수 있도록 제공하는 중앙 저장소입니다.
## 📌 개요
분산된 거래소별 종목 정보와 사용자가 식별하기 쉬운 별칭을 매핑하여 하나의 **SQLite3 데이터베이스 파일(tickers.db)**로 제공합니다.
모든 기초 데이터는 open-trading-api 저장소의 데이터를 기반으로 가공되며, 정기적으로 전체 데이터가 갱신(Full Refresh)됩니다.
## 🎯 목적
 * **빠른 조회 속도:** 수만 개의 종목 데이터를 매번 JSON/CSV로 파싱할 필요 없이, SQL 쿼리를 통해 필요한 메타데이터만 즉시 추출합니다.
 * **일관된 종목 식별:** 로컬 백테스팅 및 트레이딩 봇 실행 시, 사용자 정의 별칭(국내)과 표준 티커(해외)를 일관된 스키마로 참조할 수 있습니다.
 * **단순한 의존성:** 별도의 DB 서버 구축 없이 .db 파일 하나만 다운로드하여 로컬 파이썬 환경의 내장 sqlite3 모듈로 바로 연동합니다.
## ⚙️ 데이터 구성 방식
본 저장소는 변경 이력(Diff)을 추적하지 않고, 갱신 주기마다 기존 데이터베이스를 폐기한 후 새로운 스냅샷을 생성하는 방식을 취합니다.
### 테이블 스키마 (예정)
 * **domestic (국내 주식)**
   * alias: 사용자 정의 종목명 (예: 삼성전자)
   * symbol: 종목 번호 (6자리 코드)
   * exchange: 거래소 구분 (KOSPI, KOSDAQ 등)
 * **overseas (해외 주식)**
   * ticker: 종목 티커 (예: AAPL)
   * exchange: 거래소 구분 (NASDAQ, NYSE 등)
## 🔄 자동화 단계 (Workflow)
GitHub Actions를 통해 다음과 같은 파이프라인이 정기적으로 실행됩니다.
 1. **데이터 수집 (Fetch):** open-trading-api 저장소로부터 최신 국내/해외 티커 메타데이터를 다운로드합니다.
 2. **DB 초기화 (Reset):** 기존의 tickers.db 파일을 삭제하고 비어있는 데이터베이스와 테이블 스키마를 새로 생성합니다.
 3. **데이터 삽입 (Insert):** 수집된 데이터를 정제하여 각각의 테이블(domestic, overseas)에 벌크 인서트(Bulk Insert)합니다.
 4. **배포 (Commit & Push):** 새롭게 생성된 tickers.db 파일을 본 저장소의 main 브랜치에 덮어쓰기 커밋하여 최신 상태를 유지합니다.
**💡 Usage (Python 환경 연동 예시)**
```python
import sqlite3
import pandas as pd

# tickers.db 파일 다운로드 후 로컬 연동
conn = sqlite3.connect('tickers.db')

# 국내 삼성전자 종목코드 조회 예시
query = "SELECT symbol FROM domestic WHERE alias = '삼성전자'"
symbol = pd.read_sql(query, conn).iloc[0]['symbol']

print(f"삼성전자 종목코드: {symbol}")
conn.close()

```

​