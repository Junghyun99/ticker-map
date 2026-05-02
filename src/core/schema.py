"""tickers.db 의 단일 테이블 스키마를 정의하고 공유한다.

Python 측에서 행을 다룰 때는 :class:`Ticker` 데이터클래스를,
SQL 발행이 필요할 때는 ``CREATE_TABLE_SQL`` / ``DROP_TABLE_SQL`` /
``INSERT_SQL`` / ``COLUMNS`` 상수를 사용한다.

dataclass 의 필드 순서가 곧 ``COLUMNS`` 의 순서이며,
INSERT 시 전달하는 튜플 순서와도 일치해야 한다.
"""

from dataclasses import dataclass, fields
from typing import Optional

TABLE_NAME = "tickers"


@dataclass(frozen=True)
class Ticker:
    """tickers 테이블의 한 행을 표현한다.

    필드 순서는 SQL 컬럼 순서와 일치한다.
    """

    ticker: str            # PRIMARY KEY (국내 6자리 코드 / 해외 티커)
    exchange: str          # KS, KQ, NYS, NAS, AMS
    alias: Optional[str]   # 사용자 정의 종목명 (해외는 티커와 동일)
    asset_type: str        # Stock, ETF, ETN ...
    currency: str          # KRW, USD ...


COLUMNS: tuple[str, ...] = tuple(f.name for f in fields(Ticker))

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
