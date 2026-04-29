
# Ticker Map (ticker-map)
퀀트 투자 및 자동매매 시스템을 위한 **국내외 통합 주식 티커 및 메타데이터 중앙 저장소**입니다.
## 📌 개요
분산된 거래소별 종목 정보와 별칭(Alias)을 통합하여, 파이썬 환경에서 즉시 쿼리할 수 있는 단일 **SQLite3 데이터베이스 파일(tickers.db)**로 제공합니다.
모든 기초 데이터는 open-trading-api 저장소를 기반으로 하며, GitHub Actions를 통해 정기적으로 전체 데이터가 갱신(Full Refresh)됩니다.
## 📊 데이터베이스 스키마
자동매매 로직의 효율성을 위해 불필요한 데이터를 배제하고 핵심 메타데이터 5개 컬럼으로 구성된 단일/통합 테이블 구조를 사용합니다.
| Column | Type | Description | Example |
|---|---|---|---|
| **ticker** (PK) | TEXT | 종목 식별자 (국내: 6자리 코드, 해외: 티커) | 005930, AAPL |
| **exchange** | TEXT | 거래소 단축 코드 (하단 매핑표 참고) | KS, NAS |
| **alias** | TEXT | 사용자 정의 종목명 (해외는 티커와 동일) | 삼성전자, AAPL |
| **asset_type** | TEXT | 자산 군 분류 (Stock, ETF, ETN 등) | Stock, ETF |
| **currency** | TEXT | 거래 결제 통화 (KRW, USD 등) | KRW, USD |
### 🏛 거래소 코드 매핑 (Exchange)
시스템 내장 코드의 통일성을 위해 아래와 같이 단축된 거래소 코드를 사용합니다.
 * **국내**: KS (KOSPI), KQ (KOSDAQ)
 * **해외**: NYS (NYSE), NAS (NASDAQ), AMS (AMEX)
## 🔄 데이터 갱신 방식 (Workflow)
본 데이터베이스는 변경 이력을 추적하지 않는 '스냅샷' 방식으로 관리됩니다.
 1. **데이터 수집:** open-trading-api의 최신 메타데이터 다운로드
 2. **DB 초기화:** 기존 tickers.db 폐기 후 신규 테이블 스키마 생성
 3. **데이터 삽입:** 파이썬 스크립트를 통해 정제된 데이터를 SQLite3에 벌크 인서트(Bulk Insert)
 4. **자동 배포:** 생성된 DB 파일을 GitHub Actions가 주기적으로 커밋 및 푸시
## 🛠 Usage (Python 연동)
별도의 DB 서버 설정 없이, 저장소의 tickers.db 파일을 내려받아 파이썬 내장 라이브러리로 즉시 사용할 수 있습니다.
```python
import sqlite3
import pandas as pd

# 로컬 DB 연결
conn = sqlite3.connect('tickers.db')

# 예시: 미국(USD) ETF 목록 조회
query = """
    SELECT ticker, alias 
    FROM tickers 
    WHERE asset_type = 'ETF' AND currency = 'USD'
"""
usd_etfs = pd.read_sql(query, conn)

print(usd_etfs.head())
conn.close()

```
