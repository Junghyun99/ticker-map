"""tickers.db SQLite CRUD 캡슐화.

core 의 ``Ticker`` 도메인 객체를 받아 적재한다. SQL 상수도 이 모듈이 들고 있어
core 는 SQL 을 모르게 한다.
"""

from __future__ import annotations

import sqlite3
from dataclasses import astuple
from pathlib import Path
from typing import Iterable

from src.core.entities.ticker import COLUMNS, Ticker
from src.core.ports.repository import ITickerRepository

TABLE_NAME = "tickers"

CREATE_TABLE_SQL = f"""
CREATE TABLE {TABLE_NAME} (
    ticker     TEXT PRIMARY KEY,
    exchange   TEXT NOT NULL,
    alias      TEXT,
    asset_type TEXT NOT NULL,
    currency   TEXT NOT NULL
);
""".strip()

DROP_TABLE_SQL = f"DROP TABLE IF EXISTS {TABLE_NAME};"

INSERT_SQL = (
    f"INSERT INTO {TABLE_NAME} ({', '.join(COLUMNS)}) "
    f"VALUES ({', '.join('?' * len(COLUMNS))})"
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
