"""KOSDAQ raw 레코드(dict) → Ticker 변환 규칙. pure 함수, 외부 의존 없음."""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from src.core.entities.ticker import Ticker

KOSDAQ_ASSET_TYPE_MAP = {"ST": "Stock", "EF": "ETF"}


def normalize_kosdaq(rows: Iterable[Mapping[str, Any]]) -> list[Ticker]:
    out: list[Ticker] = []
    for r in rows:
        code = r.get("단축코드")
        group = r.get("증권그룹구분코드")
        if not code or len(code) != 6 or group not in KOSDAQ_ASSET_TYPE_MAP:
            continue
        alias = r.get("한글종목명")
        out.append(Ticker(
            ticker=code,
            exchange="KQ",
            alias=alias if alias else None,
            asset_type=KOSDAQ_ASSET_TYPE_MAP[group],
            currency="KRW",
        ))
    return out
