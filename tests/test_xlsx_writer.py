import pandas as pd
from unittest.mock import MagicMock
from src.core.entities.ticker import Ticker
from src.infra.xlsx_writer import XlsxArtifactWriter

def test_xlsx_writer_output(tmp_path):
    data_dir = tmp_path / "data"
    logger = MagicMock()
    writer = XlsxArtifactWriter(data_dir, logger)
    
    tickers = [
        Ticker("005930", "KS", "삼성전자", "Stock", "KRW"),
        Ticker("AAPL", "NAS", "AAPL", "Stock", "USD")
    ]
    
    path = writer.write("kospi", tickers)
    
    assert path.exists()
    assert path.name == "kospi_code.xlsx"
    
    # 데이터 내용 확인
    df = pd.read_excel(path)
    assert len(df) == 2
    assert df.iloc[0]["ticker"] == "005930"
    assert df.iloc[1]["ticker"] == "AAPL"
    assert list(df.columns) == ["ticker", "exchange", "alias", "asset_type", "currency"]
    
    logger.info.assert_called_once()
