from pathlib import Path
from unittest.mock import MagicMock, patch
import pandas as pd
import pytest
from src.core.logic.base import MasterDownloader
from src.core.schema import Ticker

class MockDownloader(MasterDownloader):
    @property
    def slug(self) -> str: return "mock"
    def url(self) -> str: return "http://mock.url"
    def expected_raw_columns(self) -> list[str]: return ["col1"]
    def normalize_to_schema(self, raw: pd.DataFrame) -> list[Ticker]:
        return [Ticker(t, "EX", t, "ST", "CUR") for t in raw["col1"]]
    def _extract_to_dataframe(self, archive: Path, work_dir: Path) -> pd.DataFrame:
        return pd.DataFrame({"col1": ["A", "B"]})

def test_master_downloader_run():
    logger = MagicMock()
    downloader = MockDownloader(logger)
    
    with patch.object(downloader, "_download", return_value=Path("fake.zip")):
        tickers = downloader.run()
        
    assert len(tickers) == 2
    assert tickers[0].ticker == "A"
    assert tickers[1].ticker == "B"
    logger.info.assert_called_with("[normalize] mock (2 rows)")

def test_validate_columns_success():
    logger = MagicMock()
    downloader = MockDownloader(logger)
    df = pd.DataFrame({"col1": [1, 2]})
    # 에러 없이 통과해야 함
    downloader._validate_columns(df)

def test_validate_columns_failure():
    logger = MagicMock()
    downloader = MockDownloader(logger)
    df = pd.DataFrame({"wrong_col": [1, 2]})
    with pytest.raises(ValueError, match="raw 마스터 컬럼 불일치"):
        downloader._validate_columns(df)
