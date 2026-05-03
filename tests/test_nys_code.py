from unittest.mock import MagicMock
import pandas as pd
from src.core.logic.nys_code import NysDownloader
from src.core.logic.overseas_master import SECTYPE_COL

def test_nys_normalize():
    logger = MagicMock()
    downloader = NysDownloader(logger)
    raw = pd.DataFrame(
        {
            "Symbol": ["T", "VZ"],
            "Exchange code": ["NYS", "NYS"],
            SECTYPE_COL: [2, 2],
            "currency": ["USD", "USD"],
        }
    )
    out = downloader.normalize_to_schema(raw)
    assert [t.ticker for t in out] == ["T", "VZ"]

def test_nys_properties():
    logger = MagicMock()
    downloader = NysDownloader(logger)
    assert downloader.slug == "nys"
