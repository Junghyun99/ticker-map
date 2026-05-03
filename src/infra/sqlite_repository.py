"""tickers.db SQLite CRUD 캡슐화.

다운로더가 정규화한 :class:`Ticker` 객체를 그대로 받아 적재한다.
거래소별 변환 로직은 다운로더에 있고, xlsx 산출물은 별도 어댑터가 담당하므로
이 모듈은 단순 적재만 책임진다.
"""

from __future__ import annotations

import sqlite3
from dataclasses import astuple
from pathlib import Path
from typing import Iterable

from src.core.interfaces import ITickerRepository
from src.core.schema import (
    CREATE_TABLE_SQL,
    DROP_TABLE_SQL,
    INSERT_SQL,
    TABLE_NAME,
    Ticker,
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

    def insert_many(self, tickers: Iterable[Ticker]) -> int:
        rows = [astuple(t) for t in tickers]
        with self._connect() as conn:
            cur = conn.cursor()
            cur.executemany(INSERT_SQL, rows)
            conn.commit()
        return len(rows)

    def group_summary(self) -> list[tuple]:
        with self._connect() as conn:
            return list(conn.execute(
                f"SELECT exchange, asset_type, COUNT(*) FROM {TABLE_NAME} "
                "GROUP BY exchange, asset_type ORDER BY exchange, asset_type;"
            ))

    def sample(self, limit: int = 5) -> list[tuple]:
        with self._connect() as conn:
            return list(conn.execute(f"SELECT * FROM {TABLE_NAME} LIMIT ?;", (limit,)))
