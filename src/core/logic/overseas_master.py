"""해외 거래소 공통 다운로더 (mst.cod.zip + 탭구분 파싱).

NAS/NYS/AMS 모두 컬럼·매핑·통화·exchange 출처가 동일하므로 거의 모든 동작을
이 베이스에서 처리한다. 자식은 slug 만 다르게 가진다.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.core.logic.base import DWS_BASE_URL, MasterDownloader
from src.core.schema import Ticker

OVERSEAS_RAW_COLUMNS: list[str] = [
    "National code", "Exchange id", "Exchange code", "Exchange name",
    "Symbol", "realtime symbol", "Korea name", "English name",
    "Security type(1:Index,2:Stock,3:ETP(ETF),4:Warrant)", "currency",
    "float position", "data type", "base price",
    "Bid order size", "Ask order size",
    "market start time(HHMM)", "market end time(HHMM)",
    "DR 여부(Y/N)", "DR 국가코드", "업종분류코드",
    "지수구성종목 존재 여부(0:구성종목없음,1:구성종목있음)",
    "Tick size Type",
    "구분코드(001:ETF,002:ETN,003:ETC,004:Others,005:VIX Underlying ETF,006:VIX Underlying ETN)",
    "Tick size type 상세",
]

SECTYPE_COL = "Security type(1:Index,2:Stock,3:ETP(ETF),4:Warrant)"
OVERSEAS_ASSET_TYPE_MAP = {2: "Stock", 3: "ETF"}


class OverseasMasterDownloader(MasterDownloader):
    def url(self) -> str:
        return f"{DWS_BASE_URL}/{self.slug}mst.cod.zip"

    def expected_raw_columns(self) -> list[str]:
        return OVERSEAS_RAW_COLUMNS

    def _extract_to_dataframe(self, archive: Path, work_dir: Path) -> pd.DataFrame:
        # .cod 파일은 첫 줄에 영문 헤더가 있어 read_table 이 자동 추출한다.
        # 헤더 일치 여부는 _validate_columns() 가 expected_raw_columns() 와 비교해 검증.
        cod_path = self._extract_zip(archive, work_dir, suffix=".cod")
        return pd.read_table(cod_path, sep="\t", encoding="cp949")

    def normalize_to_schema(self, raw: pd.DataFrame) -> list[Ticker]:
        df = raw.dropna(subset=["Symbol", SECTYPE_COL, "Exchange code", "currency"])
        df = df[df[SECTYPE_COL].isin(OVERSEAS_ASSET_TYPE_MAP)]
        return [
            Ticker(
                ticker=symbol,
                exchange=exchange,
                alias=symbol,
                asset_type=OVERSEAS_ASSET_TYPE_MAP[sectype],
                currency=currency,
            )
            for symbol, exchange, sectype, currency in zip(
                df["Symbol"].values,
                df["Exchange code"].values,
                df[SECTYPE_COL].values,
                df["currency"].values,
            )
        ]
