from pathlib import Path
from unittest.mock import MagicMock, patch
import pandas as pd
import pytest
from src.core.logic.overseas_master import OverseasMasterDownloader
from src.core.schema import Ticker

class MockOverseasDownloader(OverseasMasterDownloader):
    @property
    def slug(self) -> str: return "mock_os"

def test_overseas_master_extract_to_dataframe(tmp_path):
    logger = MagicMock()
    downloader = MockOverseasDownloader(logger)
    
    # Overseas master uses tab-separated .cod files
    # We need to provide at least as many columns as OVERSEAS_RAW_COLUMNS (24 columns)
    cols = downloader.expected_raw_columns()
    data = ["val"] * len(cols)
    data[cols.index("Symbol")] = "AAPL"
    data[cols.index("Exchange code")] = "NAS"
    
    cod_content = "\t".join(data) + "\n"
    cod_file = tmp_path / "mock_os.cod"
    cod_file.write_text(cod_content, encoding="cp949")
    
    with patch.object(downloader, "_extract_zip", return_value=cod_file):
        df = downloader._extract_to_dataframe(Path("fake.zip"), tmp_path)
    
    assert len(df) == 1
    assert df.iloc[0]["Symbol"] == "AAPL"
    assert df.iloc[0]["Exchange code"] == "NAS"
