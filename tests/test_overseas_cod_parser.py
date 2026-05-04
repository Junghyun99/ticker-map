from src.infra.overseas_cod_parser import OVERSEAS_RAW_COLUMNS, OverseasCodParser, SECTYPE_COL


def _build_cod_line(values: list) -> str:
    """OVERSEAS_RAW_COLUMNS 길이만큼 채워 탭으로 join 한다. 짧으면 빈문자열로 패딩."""
    padded = list(values) + [""] * (len(OVERSEAS_RAW_COLUMNS) - len(values))
    return "\t".join(str(v) for v in padded)


def test_overseas_parser_basic():
    # National code, Exchange id, Exchange code, Exchange name, Symbol, ..., currency 까지 채움
    fields = [
        "840", "1", "NAS", "NASDAQ",
        "AAPL", "AAPL", "애플", "Apple Inc",
        "2",   # Security type
        "USD", # currency
    ]
    line = _build_cod_line(fields)
    content = line.encode("cp949")

    rows = OverseasCodParser().parse(content, "nas")
    assert len(rows) == 1
    r = rows[0]
    assert r["Symbol"] == "AAPL"
    assert r["Exchange code"] == "NAS"
    assert r["currency"] == "USD"
    assert r[SECTYPE_COL] == 2  # int 캐스팅 확인


def test_overseas_parser_sectype_invalid_becomes_none():
    fields = ["840", "1", "NAS", "NASDAQ", "FOO", "FOO", "", "", "abc", "USD"]
    content = _build_cod_line(fields).encode("cp949")
    rows = OverseasCodParser().parse(content, "nas")
    assert rows[0][SECTYPE_COL] is None


def test_overseas_parser_skips_blank_lines():
    line1 = _build_cod_line(["840", "1", "NAS", "NASDAQ", "AAPL", "AAPL", "", "", "2", "USD"])
    content = (line1 + "\n\n\n").encode("cp949")
    rows = OverseasCodParser().parse(content, "nas")
    assert len(rows) == 1


def test_overseas_parser_multiple_lines():
    line1 = _build_cod_line(["840", "1", "NAS", "NASDAQ", "AAPL", "AAPL", "", "", "2", "USD"])
    line2 = _build_cod_line(["840", "1", "NAS", "NASDAQ", "QQQ", "QQQ", "", "", "3", "USD"])
    content = (line1 + "\n" + line2).encode("cp949")
    rows = OverseasCodParser().parse(content, "nas")
    assert len(rows) == 2
    assert rows[0]["Symbol"] == "AAPL"
    assert rows[1]["Symbol"] == "QQQ"
    assert rows[1][SECTYPE_COL] == 3
