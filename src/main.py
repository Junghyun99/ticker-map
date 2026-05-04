"""5거래소 마스터 데이터를 다운로드해 정규화 엑셀로 저장하고 tickers.db 에 적재한다.

main.py 는 컴포지션 루트만 담당한다. 비즈니스 로직 없음.
"""

import os

from src.config import Config
from src.core.normalizers.kosdaq import normalize_kosdaq
from src.core.normalizers.kospi import normalize_kospi
from src.core.normalizers.overseas import normalize_overseas
from src.core.sources import ALL_SOURCES
from src.core.use_cases.rebuild_ticker_db import RebuildTickerDb
from src.infra.http_requests_fetcher import HttpRequestsFetcher
from src.infra.kr_mst_parser import KrMstParser
from src.infra.kst_logger import KstLogger
from src.infra.overseas_cod_parser import OverseasCodParser
from src.infra.slack_notifier import SlackNotifier
from src.infra.sqlite_repository import SqliteTickerRepository
from src.infra.xlsx_writer import XlsxArtifactWriter
from src.infra.zip_extractor import ZipExtractor


def main() -> None:
    config = Config()
    logger = KstLogger(log_dir=config.LOG_PATH, run_number=os.getenv("GITHUB_RUN_NUMBER"))
    notifier = SlackNotifier(webhook_url=config.SLACK_WEBHOOK_URL, logger=logger)

    use_case = RebuildTickerDb(
        fetcher=HttpRequestsFetcher(),
        extractor=ZipExtractor(),
        parsers={"kr_mst": KrMstParser(), "overseas_cod": OverseasCodParser()},
        normalizers={
            "kospi": normalize_kospi,
            "kosdaq": normalize_kosdaq,
            "overseas": normalize_overseas,
        },
        repo=SqliteTickerRepository(config.DB_PATH),
        xlsx_writer=XlsxArtifactWriter(config.DATA_PATH, logger),
        logger=logger,
        notifier=notifier,
    )

    try:
        n = use_case.execute(ALL_SOURCES)
        notifier.send_message(f"[ticker-map] 완료: {n}건 insert")
    except Exception as e:
        logger.error(f"[main] failed: {e}")
        notifier.send_alert(f"[ticker-map] 실패: {e}")
        raise


if __name__ == "__main__":
    main()
