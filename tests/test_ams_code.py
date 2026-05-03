from unittest.mock import MagicMock
import pandas as pd
from src.core.logic.ams_code import AmsDownloader
from src.core.logic.overseas_master import SECTYPE_COL

def test_ams_normalize():
    logger = MagicMock()
    downloader = AmsDownloader(logger)
    raw = pd.DataFrame(
        {
            "Symbol": ["ASML", "ADYEN"],
            "Exchange code": ["AMS", "AMS"],
            SECTYPE_COL: [2, 2],
            "currency": ["EUR", "EUR"],
        }
    )
    out = downloader.normalize_to_schema(raw)
    assert [t.ticker for t in out] == ["ASML", "ADYEN"]

def test_ams_properties():
    logger = MagicMock()
    downloader = AmsDownloader(logger)
    assert downloader.slug == "ams"
