"""KOSPI(KS) 마스터 다운로더.

KrMasterDownloader 의 템플릿을 따르며, 이 파일에는 KOSPI 의 차이점만 담는다:
URL slug, 고정폭 byte_size, part1/part2 컬럼명과 field_specs, 한글→스키마 매핑.
"""

from __future__ import annotations

import pandas as pd

from src.core.logic.kr_master import KrMasterDownloader
from src.core.schema import Ticker

KOSPI_BYTE_SIZE = 228

KOSPI_PART1_COLUMNS = ["단축코드", "표준코드", "한글명"]

KOSPI_FIELD_SPECS = [
    2, 1, 4, 4, 4,
    1, 1, 1, 1, 1,
    1, 1, 1, 1, 1,
    1, 1, 1, 1, 1,
    1, 1, 1, 1, 1,
    1, 1, 1, 1, 1,
    1, 9, 5, 5, 1,
    1, 1, 2, 1, 1,
    1, 2, 2, 2, 3,
    1, 3, 12, 12, 8,
    15, 21, 2, 7, 1,
    1, 1, 1, 1, 9,
    9, 9, 5, 9, 8,
    9, 3, 1, 1, 1,
]

KOSPI_PART2_COLUMNS = [
    "그룹코드", "시가총액규모", "지수업종대분류", "지수업종중분류", "지수업종소분류",
    "제조업", "저유동성", "지배구조지수종목", "KOSPI200섹터업종", "KOSPI100",
    "KOSPI50", "KRX", "ETP", "ELW발행", "KRX100",
    "KRX자동차", "KRX반도체", "KRX바이오", "KRX은행", "SPAC",
    "KRX에너지화학", "KRX철강", "단기과열", "KRX미디어통신", "KRX건설",
    "Non1", "KRX증권", "KRX선박", "KRX섹터_보험", "KRX섹터_운송",
    "SRI", "기준가", "매매수량단위", "시간외수량단위", "거래정지",
    "정리매매", "관리종목", "시장경고", "경고예고", "불성실공시",
    "우회상장", "락구분", "액면변경", "증자구분", "증거금비율",
    "신용가능", "신용기간", "전일거래량", "액면가", "상장일자",
    "상장주수", "자본금", "결산월", "공모가", "우선주",
    "공매도과열", "이상급등", "KRX300", "KOSPI", "매출액",
    "영업이익", "경상이익", "당기순이익", "ROE", "기준년월",
    "시가총액", "그룹사코드", "회사신용한도초과", "담보대출가능", "대주가능",
]

KOSPI_ASSET_TYPE_MAP = {"ST": "Stock", "EF": "ETF"}


class KospiDownloader(KrMasterDownloader):
    @property
    def slug(self) -> str: return "kospi"

    @property
    def byte_size(self) -> int: return KOSPI_BYTE_SIZE

    @property
    def part1_columns(self) -> list[str]: return KOSPI_PART1_COLUMNS

    @property
    def field_specs(self) -> list[int]: return KOSPI_FIELD_SPECS

    @property
    def part2_columns(self) -> list[str]: return KOSPI_PART2_COLUMNS

    def normalize_to_schema(self, raw: pd.DataFrame) -> list[Ticker]:
        df = raw.dropna(subset=["단축코드", "그룹코드"])
        df = df[df["그룹코드"].isin(KOSPI_ASSET_TYPE_MAP)]
        df = df[df["단축코드"].str.len() == 6]
        return [
            Ticker(
                ticker=ticker,
                exchange="KS",
                alias=(alias if pd.notna(alias) else None),
                asset_type=KOSPI_ASSET_TYPE_MAP[group],
                currency="KRW",
            )
            for ticker, alias, group in zip(
                df["단축코드"].values,
                df["한글명"].values,
                df["그룹코드"].values,
            )
        ]
