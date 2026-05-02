"""kospi_code.xlsx, kosdaq_code.xlsx 를 읽어 README 스키마에 맞춘 tickers.db(SQLite) 를 생성한다.

스키마: ticker(PK), exchange, alias, asset_type, currency
필터: 그룹코드 ∈ {ST, EF}, 단축코드 길이 == 6 (KOSDAQ도 동일 정책)
매핑: ST -> Stock, EF -> ETF, currency='KRW', alias=한글명
exchange: KOSPI -> 'KS', KOSDAQ -> 'KQ'
"""

import os
import sqlite3
from src.config import Config
import pandas as pd

from src.core.schema import (
    COLUMNS,
    CREATE_TABLE_SQL,
    DROP_TABLE_SQL,
    INSERT_SQL,
    TABLE_NAME,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "tickers.db")
KOSPI_XLSX = os.path.join(BASE_DIR, "kospi_code.xlsx")
KOSDAQ_XLSX = os.path.join(BASE_DIR, "kosdaq_code.xlsx")
NAS_XLSX = os.path.join(BASE_DIR, "nas_code.xlsx")
NYS_XLSX = os.path.join(BASE_DIR, "nys_code.xlsx")
AMS_XLSX = os.path.join(BASE_DIR, "ams_code.xlsx")

ASSET_TYPE_MAP = {"ST": "Stock", "EF": "ETF"}
OVERSEAS_ASSET_TYPE_MAP = {2: "Stock", 3: "ETF"}


def load_kospi(xlsx_path: str) -> pd.DataFrame:
    raw = pd.read_excel(
        xlsx_path,
        usecols=["단축코드", "한글명", "그룹코드"],
        dtype={"단축코드": str, "그룹코드": str, "한글명": str},
    )
    df = raw.dropna()
    df = df[df["그룹코드"].isin(ASSET_TYPE_MAP)]
    df = df[df["단축코드"].str.len() == 6]

    out = pd.DataFrame({
        "ticker": df["단축코드"].values,
        "exchange": "KS",
        "alias": df["한글명"].values,
        "asset_type": df["그룹코드"].map(ASSET_TYPE_MAP).values,
        "currency": "KRW",
    })
    return out[list(COLUMNS)]


def load_kosdaq(xlsx_path: str) -> pd.DataFrame:
    raw = pd.read_excel(
        xlsx_path,
        usecols=["단축코드", "한글종목명", "증권그룹구분코드"],
        dtype={"단축코드": str, "증권그룹구분코드": str, "한글종목명": str},
    )
    raw = raw.rename(columns={"한글종목명": "한글명", "증권그룹구분코드": "그룹코드"})
    df = raw.dropna()
    df = df[df["그룹코드"].isin(ASSET_TYPE_MAP)]
    df = df[df["단축코드"].str.len() == 6]

    out = pd.DataFrame({
        "ticker": df["단축코드"].values,
        "exchange": "KQ",
        "alias": df["한글명"].values,
        "asset_type": df["그룹코드"].map(ASSET_TYPE_MAP).values,
        "currency": "KRW",
    })
    return out[list(COLUMNS)]


def load_nas(xlsx_path: str) -> pd.DataFrame:
    raw = pd.read_excel(
        xlsx_path,
        usecols=["Symbol", "Exchange code", "Security type(1:Index,2:Stock,3:ETP(ETF),4:Warrant)", "currency"],
        dtype={"Symbol": str, "Exchange code": str, "Security type(1:Index,2:Stock,3:ETP(ETF),4:Warrant)": int, "currency": str},
    )
    df = raw.dropna()
    df = df[df["Security type(1:Index,2:Stock,3:ETP(ETF),4:Warrant)"].isin(OVERSEAS_ASSET_TYPE_MAP)]

    out = pd.DataFrame({
        "ticker": df["Symbol"].values,
        "exchange": df["Exchange code"].values,
        "alias": df["Symbol"].values,  # alias를 Symbol로 설정
        "asset_type": df["Security type(1:Index,2:Stock,3:ETP(ETF),4:Warrant)"].map(OVERSEAS_ASSET_TYPE_MAP).values,
        "currency": df["currency"].values,
    })
    return out[list(COLUMNS)]


def load_nys(xlsx_path: str) -> pd.DataFrame:
    raw = pd.read_excel(
        xlsx_path,
        usecols=["Symbol", "Exchange code", "Security type(1:Index,2:Stock,3:ETP(ETF),4:Warrant)", "currency"],
        dtype={"Symbol": str, "Exchange code": str, "Security type(1:Index,2:Stock,3:ETP(ETF),4:Warrant)": int, "currency": str},
    )
    df = raw.dropna()
    df = df[df["Security type(1:Index,2:Stock,3:ETP(ETF),4:Warrant)"].isin(OVERSEAS_ASSET_TYPE_MAP)]

    out = pd.DataFrame({
        "ticker": df["Symbol"].values,
        "exchange": df["Exchange code"].values,
        "alias": df["Symbol"].values,
        "asset_type": df["Security type(1:Index,2:Stock,3:ETP(ETF),4:Warrant)"].map(OVERSEAS_ASSET_TYPE_MAP).values,
        "currency": df["currency"].values,
    })
    return out[list(COLUMNS)]


def load_ams(xlsx_path: str) -> pd.DataFrame:
    raw = pd.read_excel(
        xlsx_path,
        usecols=["Symbol", "Exchange code", "Security type(1:Index,2:Stock,3:ETP(ETF),4:Warrant)", "currency"],
        dtype={"Symbol": str, "Exchange code": str, "Security type(1:Index,2:Stock,3:ETP(ETF),4:Warrant)": int, "currency": str},
    )
    df = raw.dropna()
    df = df[df["Security type(1:Index,2:Stock,3:ETP(ETF),4:Warrant)"].isin(OVERSEAS_ASSET_TYPE_MAP)]

    out = pd.DataFrame({
        "ticker": df["Symbol"].values,
        "exchange": df["Exchange code"].values,
        "alias": df["Symbol"].values,
        "asset_type": df["Security type(1:Index,2:Stock,3:ETP(ETF),4:Warrant)"].map(OVERSEAS_ASSET_TYPE_MAP).values,
        "currency": df["currency"].values,
    })
    return out[list(COLUMNS)]


def init_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(DROP_TABLE_SQL)
    cur.execute(CREATE_TABLE_SQL)
    conn.commit()
    return conn


def bulk_insert(conn: sqlite3.Connection, df: pd.DataFrame) -> int:
    cur = conn.cursor()
    cur.executemany(INSERT_SQL, df.itertuples(index=False, name=None))
    conn.commit()
    return len(df)


def main() -> None:
    
    kospi = load_kospi(KOSPI_XLSX)
    kosdaq = load_kosdaq(KOSDAQ_XLSX)
    nas = load_nas(NAS_XLSX)
    nys = load_nys(NYS_XLSX)
    ams = load_ams(AMS_XLSX)
    print(f"[load] kospi: {len(kospi)}, kosdaq: {len(kosdaq)}, nas: {len(nas)}, nys: {len(nys)}, ams: {len(ams)}")
    df = pd.concat([kospi, kosdaq, nas, nys, ams], ignore_index=True)

    conn = init_db(DB_PATH)
    try:
        n = bulk_insert(conn, df)
        print(f"[insert] inserted: {n}")

        cur = conn.cursor()
        print("exchange | asset_type | count")
        for exchange, asset_type, count in cur.execute(
            f"SELECT exchange, asset_type, COUNT(*) FROM {TABLE_NAME} "
            "GROUP BY exchange, asset_type ORDER BY exchange, asset_type;"
        ):
            print(f"{exchange:<8} | {asset_type:<10} | {count}")

        print("sample:")
        for row in cur.execute(f"SELECT * FROM {TABLE_NAME} LIMIT 5;"):
            print("  " + " | ".join(str(v) for v in row))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
