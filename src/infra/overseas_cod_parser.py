"""해외(NAS/NYS/AMS) 마스터 .cod 파서. cp949 탭구분 → list[dict].

원본은 ``pd.read_table`` 로 자동 dtype 추론을 받았다. 본 구현은 csv 모듈로
탭구분만 처리하고, normalizer 가 사용하는 ``Security type`` 컬럼만 int 캐스팅한다.
"""

from __future__ import annotations

import csv
import io

from src.core.ports.raw_parser import IRawParser

OVERSEAS_RAW_COLUMNS: list[str] = [
    "National code", "Exchange id", "Exchange code", "Exchange name",
    "Symbol", "realtime symbol", "Korea name", "English name",
    "Security type(1:Index,2:Stock,3:ETP(ETF),4:Warrant)", "currency",
    "float position", "data type", "base price",
    "Bid order size", "Ask order size",
    "market start time(HHMM)", "market end time(HHMM)",
    "DR 여부(Y/N)", "DR 국가코드", "업종분류코드",
    "지수구성종목 존재 여부(0:구성종목없음,1:구성종목있음)",
    "Tick size Type",
    "구분코드(001:ETF,002:ETN,003:ETC,004:Others,005:VIX Underlying ETF,006:VIX Underlying ETN)",
    "Tick size type 상세",
]

SECTYPE_COL = "Security type(1:Index,2:Stock,3:ETP(ETF),4:Warrant)"


class OverseasCodParser(IRawParser):
    def parse(self, content: bytes, slug: str) -> list[dict]:
        text = content.decode("cp949")
        reader = csv.reader(io.StringIO(text), delimiter="\t")
        rows: list[dict] = []
        for fields in reader:
            if not fields or all(not f.strip() for f in fields):
                continue
            record = dict(zip(OVERSEAS_RAW_COLUMNS, fields))
            sectype = record.get(SECTYPE_COL, "").strip()
            if sectype.isdigit():
                record[SECTYPE_COL] = int(sectype)
            else:
                record[SECTYPE_COL] = None
            rows.append(record)
        return rows
