"""tickers.db SQLite CRUD 캡슐화.

엑셀이 이미 DB 스키마(ticker, exchange, alias, asset_type, currency)와 동일한
형태로 정규화되어 있다고 전제한다. 거래소별 변환 로직은 다운로더에 있으므로
이 모듈은 단순 적재만 책임진다.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from src.core.interfaces import ITickerRepository
from src.core.schema import (
    COLUMNS,
    CREATE_TABLE_SQL,
    DROP_TABLE_SQL,
    INSERT_SQL,
    TABLE_NAME,
)


class SqliteTickerRepository(ITickerRepository):
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def reset_schema(self) -> None:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(DROP_TABLE_SQL)
            cur.execute(CREATE_TABLE_SQL)
            conn.commit()

    def bulk_insert_from_xlsx_dir(self, data_dir: Path, filenames: list[str]) -> int:
        frames = [pd.read_excel(data_dir / name) for name in filenames]
        df = pd.concat(frames, ignore_index=True)
        df = df[list(COLUMNS)]
        with self._connect() as conn:
            cur = conn.cursor()
            cur.executemany(INSERT_SQL, df.itertuples(index=False, name=None))
            conn.commit()
        return len(df)

    def group_summary(self) -> list[tuple]:
        with self._connect() as conn:
            return list(conn.execute(
                f"SELECT exchange, asset_type, COUNT(*) FROM {TABLE_NAME} "
                "GROUP BY exchange, asset_type ORDER BY exchange, asset_type;"
            ))

    def sample(self, limit: int = 5) -> list[tuple]:
        with self._connect() as conn:
            return list(conn.execute(f"SELECT * FROM {TABLE_NAME} LIMIT ?;", (limit,)))
