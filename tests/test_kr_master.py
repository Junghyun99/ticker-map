from pathlib import Path
from unittest.mock import MagicMock, patch
import pandas as pd
import pytest
from src.core.logic.kr_master import KrMasterDownloader
from src.core.schema import Ticker

class MockKrDownloader(KrMasterDownloader):
    @property
    def slug(self) -> str: return "mock_kr"
    @property
    def byte_size(self) -> int: return 10
    @property
    def part1_columns(self) -> list[str]: return ["code", "std_code", "name"]
    @property
    def field_specs(self) -> list[int]: return [5, 5]
    @property
    def part2_columns(self) -> list[str]: return ["meta1", "meta2"]
    def normalize_to_schema(self, raw: pd.DataFrame) -> list[Ticker]:
        return []

def test_kr_master_extract_to_dataframe(tmp_path):
    logger = MagicMock()
    downloader = MockKrDownloader(logger)
    
    # 9 chars (code) + 12 chars (std_code) + name + 10 chars (byte_size)
    # 012345678 (code)
    # 901234567890 (std_code)
    # NAME (name)
    # 1234567890 (part2)
    line1 = "005930   KR7005930003삼성전자    META1META2"
    mst_file = tmp_path / "mock_kr.mst"
    mst_file.write_text(line1, encoding="cp949")
    
    with patch.object(downloader, "_extract_zip", return_value=mst_file):
        df = downloader._extract_to_dataframe(Path("fake.zip"), tmp_path)
    
    assert len(df) == 1
    assert df.iloc[0]["code"] == "005930"
    assert df.iloc[0]["std_code"] == "KR7005930003"
    assert df.iloc[0]["name"] == "삼성전자"
    assert df.iloc[0]["meta1"] == "META1"
    assert df.iloc[0]["meta2"] == "META2"
