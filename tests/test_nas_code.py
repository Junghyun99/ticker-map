from unittest.mock import MagicMock
import pandas as pd
from src.core.logic.nas_code import NasDownloader
from src.core.logic.overseas_master import SECTYPE_COL

def test_nas_normalize():
    logger = MagicMock()
    downloader = NasDownloader(logger)
    raw = pd.DataFrame(
        {
            "Symbol": ["AAPL", "QQQ"],
            "Exchange code": ["NAS", "NAS"],
            SECTYPE_COL: [2, 3],
            "currency": ["USD", "USD"],
        }
    )
    out = downloader.normalize_to_schema(raw)
    assert [t.ticker for t in out] == ["AAPL", "QQQ"]
    assert all(t.exchange == "NAS" for t in out)

def test_nas_properties():
    logger = MagicMock()
    downloader = NasDownloader(logger)
    assert downloader.slug == "nas"
