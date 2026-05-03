"""KOSDAQ(KQ) 마스터 다운로더.

KrMasterDownloader 의 템플릿을 따르며, 이 파일에는 KOSDAQ 의 차이점만 담는다:
URL slug, 고정폭 byte_size, KOSDAQ 만의 part1/part2 컬럼명·field_specs,
KOSDAQ 고유 alias/그룹 컬럼명(한글종목명/증권그룹구분코드) 매핑.
"""

from __future__ import annotations

import pandas as pd

from src.core.logic.kr_master import KrMasterDownloader

KOSDAQ_BYTE_SIZE = 222

KOSDAQ_PART1_COLUMNS = ["단축코드", "표준코드", "한글종목명"]

KOSDAQ_FIELD_SPECS = [
    2, 1,
    4, 4, 4, 1, 1,
    1, 1, 1, 1, 1,
    1, 1, 1, 1, 1,
    1, 1, 1, 1, 1,
    1, 1, 1, 1, 9,
    5, 5, 1, 1, 1,
    2, 1, 1, 1, 2,
    2, 2, 3, 1, 3,
    12, 12, 8, 15, 21,
    2, 7, 1, 1, 1,
    1, 9, 9, 9, 5,
    9, 8, 9, 3, 1,
    1, 1,
]

KOSDAQ_PART2_COLUMNS = [
    "증권그룹구분코드", "시가총액 규모 구분 코드 유가",
    "지수업종 대분류 코드", "지수 업종 중분류 코드", "지수업종 소분류 코드", "벤처기업 여부 (Y/N)",
    "저유동성종목 여부", "KRX 종목 여부", "ETP 상품구분코드", "KRX100 종목 여부 (Y/N)",
    "KRX 자동차 여부", "KRX 반도체 여부", "KRX 바이오 여부", "KRX 은행 여부", "기업인수목적회사여부",
    "KRX 에너지 화학 여부", "KRX 철강 여부", "단기과열종목구분코드", "KRX 미디어 통신 여부",
    "KRX 건설 여부", "(코스닥)투자주의환기종목여부", "KRX 증권 구분", "KRX 선박 구분",
    "KRX섹터지수 보험여부", "KRX섹터지수 운송여부", "KOSDAQ150지수여부 (Y,N)", "주식 기준가",
    "정규 시장 매매 수량 단위", "시간외 시장 매매 수량 단위", "거래정지 여부", "정리매매 여부",
    "관리 종목 여부", "시장 경고 구분 코드", "시장 경고위험 예고 여부", "불성실 공시 여부",
    "우회 상장 여부", "락구분 코드", "액면가 변경 구분 코드", "증자 구분 코드", "증거금 비율",
    "신용주문 가능 여부", "신용기간", "전일 거래량", "주식 액면가", "주식 상장 일자", "상장 주수(천)",
    "자본금", "결산 월", "공모 가격", "우선주 구분 코드", "공매도과열종목여부", "이상급등종목여부",
    "KRX300 종목 여부 (Y/N)", "매출액", "영업이익", "경상이익", "단기순이익", "ROE(자기자본이익률)",
    "기준년월", "전일기준 시가총액 (억)", "그룹사 코드", "회사신용한도초과여부", "담보대출가능여부", "대주가능여부",
]

KOSDAQ_ASSET_TYPE_MAP = {"ST": "Stock", "EF": "ETF"}


class KosdaqDownloader(KrMasterDownloader):
    @property
    def slug(self) -> str: return "kosdaq"

    @property
    def byte_size(self) -> int: return KOSDAQ_BYTE_SIZE

    @property
    def part1_columns(self) -> list[str]: return KOSDAQ_PART1_COLUMNS

    @property
    def field_specs(self) -> list[int]: return KOSDAQ_FIELD_SPECS

    @property
    def part2_columns(self) -> list[str]: return KOSDAQ_PART2_COLUMNS

    def normalize_to_schema(self, raw: pd.DataFrame) -> pd.DataFrame:
        df = raw.dropna(subset=["단축코드", "증권그룹구분코드"])
        df = df[df["증권그룹구분코드"].isin(KOSDAQ_ASSET_TYPE_MAP)]
        df = df[df["단축코드"].str.len() == 6]
        return pd.DataFrame(
            {
                "ticker": df["단축코드"].values,
                "exchange": "KQ",
                "alias": df["한글종목명"].values,
                "asset_type": df["증권그룹구분코드"].map(KOSDAQ_ASSET_TYPE_MAP).values,
                "currency": "KRW",
            }
        )
