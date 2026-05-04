"""KOSPI raw 레코드(dict) → Ticker 변환 규칙. pure 함수, 외부 의존 없음."""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from src.core.entities.ticker import Ticker

KOSPI_ASSET_TYPE_MAP = {"ST": "Stock", "EF": "ETF"}


def normalize_kospi(rows: Iterable[Mapping[str, Any]]) -> list[Ticker]:
    out: list[Ticker] = []
    for r in rows:
        code = r.get("단축코드")
        group = r.get("그룹코드")
        if not code or len(code) != 6 or group not in KOSPI_ASSET_TYPE_MAP:
            continue
        alias = r.get("한글명")
        out.append(Ticker(
            ticker=code,
            exchange="KS",
            alias=alias if alias else None,
            asset_type=KOSPI_ASSET_TYPE_MAP[group],
            currency="KRW",
        ))
    return out
