from unittest.mock import MagicMock
import pandas as pd
from src.core.logic.kosdaq_code import KosdaqDownloader

def test_kosdaq_normalize():
    logger = MagicMock()
    downloader = KosdaqDownloader(logger)
    raw = pd.DataFrame(
        {
            "단축코드": ["000020", "000040", "999999"],
            "한글종목명": ["A기업", None, "C기업"],
            "증권그룹구분코드": ["ST", "ST", "EF"],
        }
    )
    out = downloader.normalize_to_schema(raw)

    assert all(t.exchange == "KQ" for t in out)
    assert all(t.currency == "KRW" for t in out)
    assert [t.ticker for t in out] == ["000020", "000040", "999999"]
    assert [t.asset_type for t in out] == ["Stock", "Stock", "ETF"]
    assert [t.alias for t in out] == ["A기업", None, "C기업"]

def test_kosdaq_properties():
    logger = MagicMock()
    downloader = KosdaqDownloader(logger)
    assert downloader.slug == "kosdaq"
    assert "단축코드" in downloader.part1_columns
    assert "증권그룹구분코드" in downloader.part2_columns
