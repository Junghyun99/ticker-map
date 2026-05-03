from unittest.mock import MagicMock
import pandas as pd
from src.core.logic.kospi_code import KospiDownloader

def test_kospi_normalize():
    logger = MagicMock()
    downloader = KospiDownloader(logger)
    raw = pd.DataFrame(
        {
            "단축코드": ["000020", "000040", "TOOLONG", "999999", "111111"],
            "한글명": ["동화약품", "KR모터스", "잘못된코드", "지수상품", None],
            "그룹코드": ["ST", "ST", "ST", "EF", "ST"],
        }
    )
    out = downloader.normalize_to_schema(raw)

    assert [t.ticker for t in out] == ["000020", "000040", "999999", "111111"]
    assert all(t.exchange == "KS" for t in out)
    assert all(t.currency == "KRW" for t in out)
    assert [t.asset_type for t in out] == ["Stock", "Stock", "ETF", "Stock"]
    assert [t.alias for t in out] == ["동화약품", "KR모터스", "지수상품", None]

def test_kospi_properties():
    logger = MagicMock()
    downloader = KospiDownloader(logger)
    assert downloader.slug == "kospi"
    assert downloader.byte_size == 228
    assert "단축코드" in downloader.part1_columns
    assert "그룹코드" in downloader.part2_columns
