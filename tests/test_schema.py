from src.core.schema import Ticker, COLUMNS, CREATE_TABLE_SQL, TABLE_NAME

def test_ticker_dataclass():
    t = Ticker(
        ticker="005930",
        exchange="KS",
        alias="삼성전자",
        asset_type="Stock",
        currency="KRW"
    )
    assert t.ticker == "005930"
    assert t.exchange == "KS"
    assert t.alias == "삼성전자"
    assert t.asset_type == "Stock"
    assert t.currency == "KRW"

def test_columns_match_fields():
    expected = ("ticker", "exchange", "alias", "asset_type", "currency")
    assert COLUMNS == expected

def test_sql_constants():
    assert f"CREATE TABLE {TABLE_NAME}" in CREATE_TABLE_SQL
    assert "ticker     TEXT PRIMARY KEY" in CREATE_TABLE_SQL
