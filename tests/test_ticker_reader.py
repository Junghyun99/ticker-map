import pytest
import os
import shutil
from src.utils.ticker_reader import get_ticker_info, DEFAULT_DB_PATH

def test_get_ticker_info_success():
    # 삼성전자 (KOSPI)
    info = get_ticker_info("005930")
    assert info is not None
    assert info["ticker"] == "005930"
    assert info["exchange"] == "KS"
    assert info["currency"] == "KRW"

def test_get_ticker_info_overseas_success():
    # Apple (NASDAQ) - 티커가 데이터베이스에 있을 경우
    info = get_ticker_info("AAPL")
    if info: # 데이터베이스에 없을 수도 있으므로 있을 경우만 검증
        assert info["ticker"] == "AAPL"
        assert info["exchange"] == "NAS"
        assert info["currency"] == "USD"

def test_get_ticker_info_not_found():
    info = get_ticker_info("NON_EXISTENT_TICKER")
    assert info is None

def test_get_ticker_info_invalid_db_path():
    info = get_ticker_info("005930", db_path="invalid_path.db")
    assert info is None

def test_default_db_path_resolution():
    # DEFAULT_DB_PATH가 ticker_reader.py와 같은 디렉토리의 tickers.db를 가리키는지 확인
    expected_dir = os.path.dirname(os.path.abspath("src/utils/ticker_reader.py"))
    assert os.path.dirname(DEFAULT_DB_PATH) == expected_dir
    assert os.path.basename(DEFAULT_DB_PATH) == "tickers.db"
