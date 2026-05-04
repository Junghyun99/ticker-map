"""tickers 테이블의 한 행을 표현하는 도메인 객체.

dataclass 의 필드 순서가 곧 ``COLUMNS`` 의 순서이며, INSERT 시 전달하는
튜플 순서와도 일치해야 한다. SQL 상수는 ``infra/sqlite_repository.py`` 가
COLUMNS 를 사용해 생성한다.
"""

from dataclasses import dataclass, fields
from typing import Optional


@dataclass(frozen=True)
class Ticker:
    ticker: str            # PRIMARY KEY (국내 6자리 코드 / 해외 티커)
    exchange: str          # KS, KQ, NYS, NAS, AMS
    alias: Optional[str]   # 사용자 정의 종목명 (해외는 티커와 동일)
    asset_type: str        # Stock, ETF, ETN ...
    currency: str          # KRW, USD ...


COLUMNS: tuple[str, ...] = tuple(f.name for f in fields(Ticker))
