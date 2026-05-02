"""해외주식종목코드 정제 진입점.

실제 다운로드/파싱 로직은 master_downloader.download_overseas_master 에 통합되어 있고,
이 파일은 해외 .cod 파일의 컬럼 헤더 정의와 실행할 거래소 슬러그 목록만 담당한다.

지원 가능한 슬러그:
    nas, nys, ams (미국 — 본 ETL 의 대상)
    shs, shi, szs, szi (중국)
    tse (일본), hks (홍콩), hnx, hsx (베트남)
"""

from src.config import Config
from src.core.logic.master_downloader import download_overseas_master

OVERSEAS_COLUMNS = [
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

DEFAULT_SLUGS = ["nas", "nys", "ams"]


def main(slugs: list[str] = DEFAULT_SLUGS) -> None:
    config = Config()
    for slug in slugs:
        download_overseas_master(slug, OVERSEAS_COLUMNS, config.DATA_PATH)


if __name__ == "__main__":
    main()
