from dataclasses import fields

from src.core.entities.ticker import COLUMNS, Ticker


def test_columns_match_dataclass_field_order():
    assert COLUMNS == tuple(f.name for f in fields(Ticker))


def test_ticker_construction():
    t = Ticker(ticker="005930", exchange="KS", alias="삼성전자", asset_type="Stock", currency="KRW")
    assert t.ticker == "005930"
    assert t.alias == "삼성전자"
    assert t.currency == "KRW"
