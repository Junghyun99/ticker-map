"""5개 거래소(KOSPI, KOSDAQ, NAS, NYS, AMS)의 메타데이터를 한 곳에 선언한다.

main.py 의 load_kospi/kosdaq/nas/nys/ams 5개 함수가 공통 transformer 로 통합되며,
거래소마다 달라지는 부분(컬럼명/매핑/통화/필터)은 모두 ExchangeConfig 데이터로 표현한다.
"""

from dataclasses import dataclass, field, replace
from typing import Optional

OVERSEAS_SECTYPE_COL = "Security type(1:Index,2:Stock,3:ETP(ETF),4:Warrant)"

KR_ASSET_TYPE_MAP = {"ST": "Stock", "EF": "ETF"}
OVERSEAS_ASSET_TYPE_MAP = {2: "Stock", 3: "ETF"}


@dataclass(frozen=True)
class ExchangeConfig:
    """거래소별 다운로드/변환 규칙."""

    code: str                       # Ticker.exchange 값 (KS, KQ, NAS, NYS, AMS)
    slug: str                       # URL/파일명 토큰 (kospi, kosdaq, nas, nys, ams)
    xlsx_filename: str              # data/ 기준 파일명

    src_ticker_col: str             # 원본 ticker 컬럼명
    src_alias_col: str              # 원본 alias 컬럼명
    src_asset_type_col: str         # 원본 asset_type 컬럼명
    asset_type_map: dict            # 원본 코드 → Stock/ETF 매핑

    # 해외만 사용. KR 은 fixed_* 사용.
    src_exchange_col: Optional[str] = None
    src_currency_col: Optional[str] = None

    # KR 만 사용. 해외는 행마다 컬럼에서 가져옴.
    fixed_currency: Optional[str] = None

    # KOSDAQ 전용: 한글종목명 → 한글명, 증권그룹구분코드 → 그룹코드
    pre_rename: Optional[dict] = None

    # KR=6, 해외=None
    ticker_len_filter: Optional[int] = None

    # pd.read_excel 로 로드할 컬럼/타입 (xlsx 컬럼명 기준; pre_rename 전)
    read_usecols: list = field(default_factory=list)
    read_dtype: dict = field(default_factory=dict)


KOSPI = ExchangeConfig(
    code="KS",
    slug="kospi",
    xlsx_filename="kospi_code.xlsx",
    src_ticker_col="단축코드",
    src_alias_col="한글명",
    src_asset_type_col="그룹코드",
    asset_type_map=KR_ASSET_TYPE_MAP,
    fixed_currency="KRW",
    ticker_len_filter=6,
    read_usecols=["단축코드", "한글명", "그룹코드"],
    read_dtype={"단축코드": str, "한글명": str, "그룹코드": str},
)

KOSDAQ = ExchangeConfig(
    code="KQ",
    slug="kosdaq",
    xlsx_filename="kosdaq_code.xlsx",
    src_ticker_col="단축코드",
    src_alias_col="한글명",
    src_asset_type_col="그룹코드",
    asset_type_map=KR_ASSET_TYPE_MAP,
    fixed_currency="KRW",
    ticker_len_filter=6,
    pre_rename={"한글종목명": "한글명", "증권그룹구분코드": "그룹코드"},
    read_usecols=["단축코드", "한글종목명", "증권그룹구분코드"],
    read_dtype={"단축코드": str, "한글종목명": str, "증권그룹구분코드": str},
)

_OVERSEAS_USECOLS = ["Symbol", "Exchange code", OVERSEAS_SECTYPE_COL, "currency"]
_OVERSEAS_DTYPE = {
    "Symbol": str,
    "Exchange code": str,
    OVERSEAS_SECTYPE_COL: int,
    "currency": str,
}

NAS = ExchangeConfig(
    code="NAS",
    slug="nas",
    xlsx_filename="nas_code.xlsx",
    src_ticker_col="Symbol",
    src_alias_col="Symbol",
    src_asset_type_col=OVERSEAS_SECTYPE_COL,
    asset_type_map=OVERSEAS_ASSET_TYPE_MAP,
    src_exchange_col="Exchange code",
    src_currency_col="currency",
    read_usecols=_OVERSEAS_USECOLS,
    read_dtype=_OVERSEAS_DTYPE,
)

NYS = replace(NAS, code="NYS", slug="nys", xlsx_filename="nys_code.xlsx")
AMS = replace(NAS, code="AMS", slug="ams", xlsx_filename="ams_code.xlsx")

EXCHANGES: list[ExchangeConfig] = [KOSPI, KOSDAQ, NAS, NYS, AMS]
