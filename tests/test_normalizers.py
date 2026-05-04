from src.core.normalizers.kosdaq import normalize_kosdaq
from src.core.normalizers.kospi import normalize_kospi
from src.core.normalizers.overseas import SECTYPE_COL, normalize_overseas


def test_normalize_kospi_basic():
    rows = [
        {"단축코드": "005930", "그룹코드": "ST", "한글명": "삼성전자"},
        {"단축코드": "069500", "그룹코드": "EF", "한글명": "KODEX 200"},
    ]
    out = normalize_kospi(rows)
    assert len(out) == 2
    assert out[0].ticker == "005930"
    assert out[0].exchange == "KS"
    assert out[0].asset_type == "Stock"
    assert out[0].alias == "삼성전자"
    assert out[0].currency == "KRW"
    assert out[1].asset_type == "ETF"


def test_normalize_kospi_filters_invalid_rows():
    rows = [
        {"단축코드": "12345", "그룹코드": "ST", "한글명": "짧은코드"},   # 6자리 아님
        {"단축코드": "1234567", "그룹코드": "ST", "한글명": "긴코드"},   # 6자리 아님
        {"단축코드": "005930", "그룹코드": "XX", "한글명": "잘못된그룹"},  # 매핑외 그룹
        {"단축코드": "", "그룹코드": "ST", "한글명": "빈코드"},
        {"단축코드": None, "그룹코드": "ST", "한글명": "None코드"},
        {"그룹코드": "ST", "한글명": "코드없음"},  # 단축코드 키 누락
    ]
    assert normalize_kospi(rows) == []


def test_normalize_kospi_empty_alias_becomes_none():
    rows = [{"단축코드": "005930", "그룹코드": "ST", "한글명": ""}]
    out = normalize_kospi(rows)
    assert out[0].alias is None


def test_normalize_kosdaq_basic():
    rows = [
        {"단축코드": "247540", "증권그룹구분코드": "ST", "한글종목명": "에코프로비엠"},
    ]
    out = normalize_kosdaq(rows)
    assert len(out) == 1
    assert out[0].ticker == "247540"
    assert out[0].exchange == "KQ"
    assert out[0].asset_type == "Stock"
    assert out[0].currency == "KRW"


def test_normalize_kosdaq_filters_invalid_rows():
    rows = [
        {"단축코드": "1234", "증권그룹구분코드": "ST", "한글종목명": "짧은코드"},
        {"단축코드": "247540", "증권그룹구분코드": "XX", "한글종목명": "잘못된그룹"},
    ]
    assert normalize_kosdaq(rows) == []


def test_normalize_overseas_basic():
    rows = [
        {"Symbol": "AAPL", "Exchange code": "NAS", SECTYPE_COL: 2, "currency": "USD"},
        {"Symbol": "QQQ", "Exchange code": "NAS", SECTYPE_COL: 3, "currency": "USD"},
    ]
    out = normalize_overseas(rows)
    assert len(out) == 2
    assert out[0].ticker == "AAPL"
    assert out[0].alias == "AAPL"
    assert out[0].asset_type == "Stock"
    assert out[0].exchange == "NAS"
    assert out[1].asset_type == "ETF"


def test_normalize_overseas_filters_invalid():
    rows = [
        {"Symbol": "FOO", "Exchange code": "NAS", SECTYPE_COL: 1, "currency": "USD"},  # Index
        {"Symbol": "", "Exchange code": "NAS", SECTYPE_COL: 2, "currency": "USD"},
        {"Symbol": "BAR", "Exchange code": "", SECTYPE_COL: 2, "currency": "USD"},
        {"Symbol": "BAZ", "Exchange code": "NAS", SECTYPE_COL: None, "currency": "USD"},
        {"Symbol": "QUX", "Exchange code": "NAS", SECTYPE_COL: 2, "currency": ""},
    ]
    assert normalize_overseas(rows) == []
