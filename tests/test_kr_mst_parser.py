from src.infra.kr_mst_parser import KrMstParser, SPECS


def _build_kr_line(short_code: str, std_code: str, name: str, part2: str, byte_size: int) -> str:
    """원본 .mst 한 줄을 모방. 단축코드 9칸 + 표준코드 12칸 + 이름(가변) + part2(byte_size-1 chars + \\n).

    원본 코드는 텍스트 모드로 읽어 trailing \\n 까지 ``len(row)`` 에 포함했다.
    여기서는 \\n 1글자가 byte_size 영역에 포함되도록 part2 를 ``byte_size - 1`` 길이로 맞춘다.
    """
    assert len(part2) == byte_size - 1
    short_padded = short_code.ljust(9)
    std_padded = std_code.ljust(12)
    return f"{short_padded}{std_padded}{name}{part2}\n"


def test_kospi_parser_basic():
    spec = SPECS["kospi"]
    # part2: 첫 2칸이 그룹코드("ST"), 나머지 226칸 채움
    part2_filler = "X" * (spec.byte_size - 1 - 2)  # 225 chars
    part2 = "ST" + part2_filler  # 227 chars (= byte_size - 1)
    line = _build_kr_line("005930", "KR7005930003", "삼성전자", part2, spec.byte_size)
    content = line.encode("cp949")

    parser = KrMstParser()
    rows = parser.parse(content, "kospi")

    assert len(rows) == 1
    r = rows[0]
    assert r["단축코드"] == "005930"
    assert r["표준코드"] == "KR7005930003"
    assert r["한글명"] == "삼성전자"
    assert r["그룹코드"] == "ST"


def test_kospi_parser_skips_short_lines():
    parser = KrMstParser()
    # byte_size 이하인 짧은 줄은 스킵
    content = b"too short\n"
    assert parser.parse(content, "kospi") == []


def test_kosdaq_parser_basic():
    spec = SPECS["kosdaq"]
    # part2: 첫 2칸이 증권그룹구분코드("ST")
    part2_filler = "Y" * (spec.byte_size - 1 - 2)
    part2 = "EF" + part2_filler
    line = _build_kr_line("247540", "KR7247540008", "에코프로비엠", part2, spec.byte_size)
    content = line.encode("cp949")

    rows = KrMstParser().parse(content, "kosdaq")
    assert len(rows) == 1
    r = rows[0]
    assert r["단축코드"] == "247540"
    assert r["한글종목명"] == "에코프로비엠"
    assert r["증권그룹구분코드"] == "EF"


def test_kospi_parser_multiple_lines():
    spec = SPECS["kospi"]
    part2_filler = "Z" * (spec.byte_size - 1 - 2)
    line1 = _build_kr_line("005930", "KR7005930003", "삼성전자", "ST" + part2_filler, spec.byte_size)
    line2 = _build_kr_line("000660", "KR7000660001", "SK하이닉스", "ST" + part2_filler, spec.byte_size)
    content = (line1 + line2).encode("cp949")

    rows = KrMstParser().parse(content, "kospi")
    assert len(rows) == 2
    assert rows[0]["단축코드"] == "005930"
    assert rows[1]["단축코드"] == "000660"
