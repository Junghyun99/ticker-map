"""Raw 레코드(dict) → Ticker 리스트 변환 함수의 시그니처."""

from __future__ import annotations

from typing import Callable, Iterable, Mapping

from src.core.entities.ticker import Ticker

Normalizer = Callable[[Iterable[Mapping[str, object]]], list[Ticker]]
