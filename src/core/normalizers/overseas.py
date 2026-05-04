"""해외(NAS/NYS/AMS) raw 레코드(dict) → Ticker 변환 규칙.

Security type 컬럼은 파서가 int 로 캐스팅해 dict 에 담아준다고 가정한다.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from src.core.entities.ticker import Ticker

SECTYPE_COL = "Security type(1:Index,2:Stock,3:ETP(ETF),4:Warrant)"
OVERSEAS_ASSET_TYPE_MAP = {2: "Stock", 3: "ETF"}


def normalize_overseas(rows: Iterable[Mapping[str, Any]]) -> list[Ticker]:
    out: list[Ticker] = []
    for r in rows:
        symbol = r.get("Symbol")
        exchange = r.get("Exchange code")
        sectype = r.get(SECTYPE_COL)
        currency = r.get("currency")
        if not symbol or not exchange or not currency or sectype not in OVERSEAS_ASSET_TYPE_MAP:
            continue
        out.append(Ticker(
            ticker=symbol,
            exchange=exchange,
            alias=symbol,
            asset_type=OVERSEAS_ASSET_TYPE_MAP[sectype],
            currency=currency,
        ))
    return out
