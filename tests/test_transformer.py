"""to_ticker_df 의 거래소별 변환 동작을 fixture 로 검증한다.

리팩토링의 가장 위험도 높은 표면이 5개 load_* → 단일 transformer 통합이므로,
거래소별 입력/기대출력을 작은 fixture 로 고정해 회귀를 잡는다.
"""

import pandas as pd
import pytest

from src.core.exchanges import (
    AMS,
    KOSDAQ,
    KOSPI,
    NAS,
    NYS,
    OVERSEAS_SECTYPE_COL,
)
from src.core.schema import COLUMNS
from src.core.transformer import to_ticker_df


def _kr_raw(ticker_col: str, alias_col: str, group_col: str) -> pd.DataFrame:
    return pd.DataFrame(
        {
            ticker_col: ["000020", "000040", "TOOLONG", "999999", "111111"],
            alias_col: ["동화약품", "KR모터스", "잘못된코드", "지수상품", None],
            group_col: ["ST", "ST", "ST", "EF", "ST"],
        }
    )


def _overseas_raw() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Symbol": ["AAPL", "QQQ", "IDX", "MSFT", "WARRANT"],
            "Exchange code": ["NAS", "NAS", "NAS", "NAS", "NAS"],
            OVERSEAS_SECTYPE_COL: [2, 3, 1, 2, 4],
            "currency": ["USD", "USD", "USD", "USD", "USD"],
        }
    )


def test_kospi_transforms_to_ticker_schema():
    raw = _kr_raw("단축코드", "한글명", "그룹코드")
    out = to_ticker_df(raw, KOSPI)

    assert list(out.columns) == list(COLUMNS)
    # 6자리 + asset_type ∈ {ST, EF} + non-null 만 통과 (TOOLONG, None alias 제외)
    assert out["ticker"].tolist() == ["000020", "000040", "999999"]
    assert (out["exchange"] == "KS").all()
    assert (out["currency"] == "KRW").all()
    assert out["asset_type"].tolist() == ["Stock", "Stock", "ETF"]
    assert out["alias"].tolist() == ["동화약품", "KR모터스", "지수상품"]


def test_kosdaq_renames_columns_before_transform():
    raw = _kr_raw("단축코드", "한글종목명", "증권그룹구분코드")
    out = to_ticker_df(raw, KOSDAQ)

    assert list(out.columns) == list(COLUMNS)
    assert (out["exchange"] == "KQ").all()
    assert (out["currency"] == "KRW").all()
    # KOSDAQ 도 동일한 6자리 + ST/EF 정책
    assert out["ticker"].tolist() == ["000020", "000040", "999999"]
    assert out["asset_type"].tolist() == ["Stock", "Stock", "ETF"]


@pytest.mark.parametrize("cfg, expected_code", [(NAS, "NAS"), (NYS, "NAS"), (AMS, "NAS")])
def test_overseas_uses_dynamic_exchange_and_currency(cfg, expected_code):
    raw = _overseas_raw()
    out = to_ticker_df(raw, cfg)

    assert list(out.columns) == list(COLUMNS)
    # Security type 1(Index), 4(Warrant) 는 필터로 제외 → AAPL/QQQ/MSFT 만 남음
    assert out["ticker"].tolist() == ["AAPL", "QQQ", "MSFT"]
    assert out["alias"].tolist() == ["AAPL", "QQQ", "MSFT"]
    assert (out["exchange"] == expected_code).all()  # 데이터 컬럼에서 가져옴
    assert (out["currency"] == "USD").all()
    assert out["asset_type"].tolist() == ["Stock", "ETF", "Stock"]


def test_overseas_drops_null_rows():
    raw = pd.DataFrame(
        {
            "Symbol": ["AAPL", None, "MSFT"],
            "Exchange code": ["NAS", "NAS", "NAS"],
            OVERSEAS_SECTYPE_COL: [2, 2, 2],
            "currency": ["USD", "USD", "USD"],
        }
    )
    out = to_ticker_df(raw, NAS)
    assert out["ticker"].tolist() == ["AAPL", "MSFT"]


def test_kr_filters_non_st_ef_group_codes():
    raw = pd.DataFrame(
        {
            "단축코드": ["000020", "000040", "000050"],
            "한글명": ["A", "B", "C"],
            "그룹코드": ["ST", "RT", "EF"],  # RT 는 매핑되지 않음 → 제외
        }
    )
    out = to_ticker_df(raw, KOSPI)
    assert out["ticker"].tolist() == ["000020", "000050"]
    assert out["asset_type"].tolist() == ["Stock", "ETF"]
