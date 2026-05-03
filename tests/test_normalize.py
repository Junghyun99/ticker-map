"""각 Downloader 의 normalize_to_schema 동작을 raw fixture 로 검증한다.

리팩토링의 가장 위험도 높은 표면은 거래소별 raw → DB 스키마 매핑이므로,
fixture 로 거래소별 입력/기대출력을 고정해 회귀를 잡는다. 다운로드/압축해제는
template 메서드의 다른 단계라 별도 테스트.
"""

from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import pytest

from src.core.logic.ams_code import AmsDownloader
from src.core.logic.kosdaq_code import KosdaqDownloader
from src.core.logic.kospi_code import KospiDownloader
from src.core.logic.nas_code import NasDownloader
from src.core.logic.nys_code import NysDownloader
from src.core.logic.overseas_master import SECTYPE_COL
from src.core.schema import COLUMNS


@pytest.fixture
def fake_logger() -> MagicMock:
    return MagicMock()


def _make(downloader_cls, fake_logger):
    return downloader_cls(Path("/tmp"), fake_logger)


def test_kospi_normalize(fake_logger):
    raw = pd.DataFrame(
        {
            "단축코드": ["000020", "000040", "TOOLONG", "999999", "111111"],
            "한글명": ["동화약품", "KR모터스", "잘못된코드", "지수상품", None],
            "그룹코드": ["ST", "ST", "ST", "EF", "ST"],
        }
    )
    out = _make(KospiDownloader, fake_logger).normalize_to_schema(raw)

    assert list(out.columns) == list(COLUMNS)
    # 6자리 + ST/EF 만 통과 (TOOLONG 제외). alias 는 Optional 이라 None 도 유지.
    assert out["ticker"].tolist() == ["000020", "000040", "999999", "111111"]
    assert (out["exchange"] == "KS").all()
    assert (out["currency"] == "KRW").all()
    assert out["asset_type"].tolist() == ["Stock", "Stock", "ETF", "Stock"]


def test_kosdaq_normalize_uses_kosdaq_specific_columns(fake_logger):
    raw = pd.DataFrame(
        {
            "단축코드": ["000020", "000040", "999999"],
            "한글종목명": ["A기업", None, "C기업"],
            "증권그룹구분코드": ["ST", "ST", "EF"],
        }
    )
    out = _make(KosdaqDownloader, fake_logger).normalize_to_schema(raw)

    assert list(out.columns) == list(COLUMNS)
    assert (out["exchange"] == "KQ").all()
    assert (out["currency"] == "KRW").all()
    assert out["ticker"].tolist() == ["000020", "000040", "999999"]
    assert out["asset_type"].tolist() == ["Stock", "Stock", "ETF"]


def test_kr_filters_non_st_ef_group_codes(fake_logger):
    raw = pd.DataFrame(
        {
            "단축코드": ["000020", "000040", "000050"],
            "한글명": ["A", "B", "C"],
            "그룹코드": ["ST", "RT", "EF"],  # RT 는 매핑 없음 → 제외
        }
    )
    out = _make(KospiDownloader, fake_logger).normalize_to_schema(raw)
    assert out["ticker"].tolist() == ["000020", "000050"]
    assert out["asset_type"].tolist() == ["Stock", "ETF"]


@pytest.mark.parametrize("downloader_cls", [NasDownloader, NysDownloader, AmsDownloader])
def test_overseas_uses_dynamic_exchange_and_currency(downloader_cls, fake_logger):
    raw = pd.DataFrame(
        {
            "Symbol": ["AAPL", "QQQ", "IDX", "MSFT", "WARRANT"],
            "Exchange code": ["NAS", "NAS", "NAS", "NAS", "NAS"],
            SECTYPE_COL: [2, 3, 1, 2, 4],  # 1=Index, 4=Warrant 는 필터 제외
            "currency": ["USD", "USD", "USD", "USD", "USD"],
        }
    )
    out = _make(downloader_cls, fake_logger).normalize_to_schema(raw)

    assert list(out.columns) == list(COLUMNS)
    assert out["ticker"].tolist() == ["AAPL", "QQQ", "MSFT"]
    assert out["alias"].tolist() == ["AAPL", "QQQ", "MSFT"]
    # exchange/currency 는 데이터 컬럼에서 가져옴
    assert (out["exchange"] == "NAS").all()
    assert (out["currency"] == "USD").all()
    assert out["asset_type"].tolist() == ["Stock", "ETF", "Stock"]


def test_overseas_drops_rows_with_null_required_fields(fake_logger):
    raw = pd.DataFrame(
        {
            "Symbol": ["AAPL", None, "MSFT", "GOOG"],
            "Exchange code": ["NAS", "NAS", "NAS", None],
            SECTYPE_COL: [2, 2, 2, 2],
            "currency": ["USD", "USD", None, "USD"],
        }
    )
    out = _make(NasDownloader, fake_logger).normalize_to_schema(raw)
    assert out["ticker"].tolist() == ["AAPL"]


def test_validate_columns_raises_on_missing_expected_columns(fake_logger):
    """방어 동작: 사전정의 컬럼이 raw 에 없으면 즉시 ValueError."""
    d = _make(KospiDownloader, fake_logger)
    raw = pd.DataFrame({"단축코드": ["000020"], "한글명": ["A"]})  # 그룹코드 누락
    with pytest.raises(ValueError, match="raw 마스터 컬럼 불일치"):
        d._validate_columns(raw)
