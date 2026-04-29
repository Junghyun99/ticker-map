"""kospi_code.xlsx 를 읽어 README 스키마에 맞춘 tickers.db(SQLite) 를 생성한다.

스키마: ticker(PK), exchange, alias, asset_type, currency
필터: 그룹코드 ∈ {ST, EF}, 단축코드 길이 == 6
매핑: ST -> Stock, EF -> ETF, exchange='KS', currency='KRW', alias=한글명
"""

import os
import sqlite3

import pandas as pd

from schema import (
    COLUMNS,
    CREATE_TABLE_SQL,
    DROP_TABLE_SQL,
    INSERT_SQL,
    TABLE_NAME,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "tickers.db")
KOSPI_XLSX = os.path.join(BASE_DIR, "kospi_code.xlsx")

ASSET_TYPE_MAP = {"ST": "Stock", "EF": "ETF"}


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
    df = load_kospi(KOSPI_XLSX)
    print(f"[load] kospi rows after filter: {len(df)}")

    conn = init_db(DB_PATH)
    try:
        n = bulk_insert(conn, df)
        print(f"[insert] inserted: {n}")

        cur = conn.cursor()
        print("asset_type | count")
        for asset_type, count in cur.execute(
            f"SELECT asset_type, COUNT(*) FROM {TABLE_NAME} "
            "GROUP BY asset_type ORDER BY asset_type;"
        ):
            print(f"{asset_type:<10} | {count}")

        print("sample:")
        for row in cur.execute(f"SELECT * FROM {TABLE_NAME} LIMIT 5;"):
            print("  " + " | ".join(str(v) for v in row))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
