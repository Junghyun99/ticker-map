"""KR(KOSPI/KOSDAQ) 마스터 .mst 파서. cp949 고정폭 → list[dict].

slug 별 (byte_size, part1_columns, part2_columns, field_specs) 매핑을 보유한다.
원본은 pandas 의 ``pd.read_fwf`` + 임시파일을 사용했지만, 본 구현은 표준 라이브러리만으로
같은 슬라이싱·rstrip 동작을 재현한다.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.core.ports.raw_parser import IRawParser

KOSPI_PART1_COLUMNS = ["단축코드", "표준코드", "한글명"]
KOSPI_PART2_COLUMNS = [
    "그룹코드", "시가총액규모", "지수업종대분류", "지수업종중분류", "지수업종소분류",
    "제조업", "저유동성", "지배구조지수종목", "KOSPI200섹터업종", "KOSPI100",
    "KOSPI50", "KRX", "ETP", "ELW발행", "KRX100",
    "KRX자동차", "KRX반도체", "KRX바이오", "KRX은행", "SPAC",
    "KRX에너지화학", "KRX철강", "단기과열", "KRX미디어통신", "KRX건설",
    "Non1", "KRX증권", "KRX선박", "KRX섹터_보험", "KRX섹터_운송",
    "SRI", "기준가", "매매수량단위", "시간외수량단위", "거래정지",
    "정리매매", "관리종목", "시장경고", "경고예고", "불성실공시",
    "우회상장", "락구분", "액면변경", "증자구분", "증거금비율",
    "신용가능", "신용기간", "전일거래량", "액면가", "상장일자",
    "상장주수", "자본금", "결산월", "공모가", "우선주",
    "공매도과열", "이상급등", "KRX300", "KOSPI", "매출액",
    "영업이익", "경상이익", "당기순이익", "ROE", "기준년월",
    "시가총액", "그룹사코드", "회사신용한도초과", "담보대출가능", "대주가능",
]
KOSPI_FIELD_SPECS = [
    2, 1, 4, 4, 4,
    1, 1, 1, 1, 1,
    1, 1, 1, 1, 1,
    1, 1, 1, 1, 1,
    1, 1, 1, 1, 1,
    1, 1, 1, 1, 1,
    1, 9, 5, 5, 1,
    1, 1, 2, 1, 1,
    1, 2, 2, 2, 3,
    1, 3, 12, 12, 8,
    15, 21, 2, 7, 1,
    1, 1, 1, 1, 9,
    9, 9, 5, 9, 8,
    9, 3, 1, 1, 1,
]

KOSDAQ_PART1_COLUMNS = ["단축코드", "표준코드", "한글종목명"]
KOSDAQ_PART2_COLUMNS = [
    "증권그룹구분코드", "시가총액 규모 구분 코드 유가",
    "지수업종 대분류 코드", "지수 업종 중분류 코드", "지수업종 소분류 코드", "벤처기업 여부 (Y/N)",
    "저유동성종목 여부", "KRX 종목 여부", "ETP 상품구분코드", "KRX100 종목 여부 (Y/N)",
    "KRX 자동차 여부", "KRX 반도체 여부", "KRX 바이오 여부", "KRX 은행 여부", "기업인수목적회사여부",
    "KRX 에너지 화학 여부", "KRX 철강 여부", "단기과열종목구분코드", "KRX 미디어 통신 여부",
    "KRX 건설 여부", "(코스닥)투자주의환기종목여부", "KRX 증권 구분", "KRX 선박 구분",
    "KRX섹터지수 보험여부", "KRX섹터지수 운송여부", "KOSDAQ150지수여부 (Y,N)", "주식 기준가",
    "정규 시장 매매 수량 단위", "시간외 시장 매매 수량 단위", "거래정지 여부", "정리매매 여부",
    "관리 종목 여부", "시장 경고 구분 코드", "시장 경고위험 예고 여부", "불성실 공시 여부",
    "우회 상장 여부", "락구분 코드", "액면가 변경 구분 코드", "증자 구분 코드", "증거금 비율",
    "신용주문 가능 여부", "신용기간", "전일 거래량", "주식 액면가", "주식 상장 일자", "상장 주수(천)",
    "자본금", "결산 월", "공모 가격", "우선주 구분 코드", "공매도과열종목여부", "이상급등종목여부",
    "KRX300 종목 여부 (Y/N)", "매출액", "영업이익", "경상이익", "단기순이익", "ROE(자기자본이익률)",
    "기준년월", "전일기준 시가총액 (억)", "그룹사 코드", "회사신용한도초과여부", "담보대출가능여부", "대주가능여부",
]
KOSDAQ_FIELD_SPECS = [
    2, 1,
    4, 4, 4, 1, 1,
    1, 1, 1, 1, 1,
    1, 1, 1, 1, 1,
    1, 1, 1, 1, 1,
    1, 1, 1, 1, 9,
    5, 5, 1, 1, 1,
    2, 1, 1, 1, 2,
    2, 2, 3, 1, 3,
    12, 12, 8, 15, 21,
    2, 7, 1, 1, 1,
    1, 9, 9, 9, 5,
    9, 8, 9, 3, 1,
    1, 1,
]


@dataclass(frozen=True)
class _KrSpec:
    byte_size: int
    part1_columns: list[str]
    part2_columns: list[str]
    field_specs: list[int]


SPECS: dict[str, _KrSpec] = {
    "kospi": _KrSpec(228, KOSPI_PART1_COLUMNS, KOSPI_PART2_COLUMNS, KOSPI_FIELD_SPECS),
    "kosdaq": _KrSpec(222, KOSDAQ_PART1_COLUMNS, KOSDAQ_PART2_COLUMNS, KOSDAQ_FIELD_SPECS),
}


class KrMstParser(IRawParser):
    def parse(self, content: bytes, slug: str) -> list[dict]:
        spec = SPECS[slug]
        text = content.decode("cp949")
        rows: list[dict] = []
        # 원본이 텍스트 모드로 파일을 순회하며 ``len(row)`` 에 trailing ``\n`` 까지 포함했던
        # 동작을 재현한다.
        for line in text.splitlines():
            row = line + "\n"
            if len(row) <= spec.byte_size:
                continue
            front_end = len(row) - spec.byte_size
            rf1 = row[:front_end]
            record: dict = {
                spec.part1_columns[0]: rf1[0:9].rstrip(),
                spec.part1_columns[1]: rf1[9:21].rstrip(),
                spec.part1_columns[2]: rf1[21:].strip(),
            }
            part2_section = row[-spec.byte_size:]
            pos = 0
            for width, name in zip(spec.field_specs, spec.part2_columns):
                record[name] = part2_section[pos:pos + width].rstrip()
                pos += width
            rows.append(record)
        return rows
