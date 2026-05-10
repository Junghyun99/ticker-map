"""Ticker 리스트를 거래소별 csv 파일로 저장하는 인프라 어댑터.

워크플로(.github/workflows/update_master_data.yml)가 tickers.db 와 함께 커밋하는
공식 산출물(data/{slug}_code.csv)을 생성한다. 컬럼 순서는 entities.ticker.COLUMNS 로 강제.
"""

from __future__ import annotations

from dataclasses import astuple
from pathlib import Path
from typing import Iterable

import pandas as pd

from src.core.entities.ticker import COLUMNS, Ticker
from src.core.ports.artifact_writer import IArtifactWriter
from src.core.ports.logger import ILogger


class CsvArtifactWriter(IArtifactWriter):
    def __init__(self, data_dir: Path, logger: ILogger) -> None:
        self.data_dir = data_dir
        self.logger = logger

    def write(self, slug: str, tickers: Iterable[Ticker]) -> Path:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        rows = [astuple(t) for t in tickers]
        df = pd.DataFrame(rows, columns=list(COLUMNS))
        csv_path = self.data_dir / f"{slug}_code.csv"
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        self.logger.info(f"[csv] {csv_path} ({len(df)} rows)")
        return csv_path
