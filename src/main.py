"""5거래소 마스터 데이터를 다운로드해 정규화 엑셀로 저장하고 tickers.db 에 적재한다.

main.py 는 조립과 실행만 담당한다. 비즈니스 로직 없음.
"""

import os

from src.config import Config
from src.core.logic.ams_code import AmsDownloader
from src.core.logic.base import MasterDownloader
from src.core.logic.kosdaq_code import KosdaqDownloader
from src.core.logic.kospi_code import KospiDownloader
from src.core.logic.nas_code import NasDownloader
from src.core.logic.nys_code import NysDownloader
from src.core.schema import Ticker
from src.infra.logger import ConverterLogger
from src.infra.notifier import SlackNotifier
from src.infra.sqlite_repository import SqliteTickerRepository
from src.infra.xlsx_writer import XlsxArtifactWriter


class App:
    def __init__(self) -> None:
        self.config = Config()
        run_number = os.getenv("GITHUB_RUN_NUMBER")
        self.logger = ConverterLogger(log_dir=self.config.LOG_PATH, run_number=run_number)
        self.notifier = SlackNotifier(webhook_url=self.config.SLACK_WEBHOOK_URL, logger=self.logger)
        self.repo = SqliteTickerRepository(self.config.DB_PATH)
        self.xlsx_writer = XlsxArtifactWriter(self.config.DATA_PATH, self.logger)
        self.downloaders: list[MasterDownloader] = [
            KospiDownloader(self.logger),
            KosdaqDownloader(self.logger),
            NasDownloader(self.logger),
            NysDownloader(self.logger),
            AmsDownloader(self.logger),
        ]
        # 항상 새 데이터로 만든다.
        self.repo.reset_schema()

    def run(self) -> None:
        try:
            all_tickers: list[Ticker] = []
            for d in self.downloaders:
                tickers = d.run()
                self.xlsx_writer.write(d.slug, tickers)
                all_tickers.extend(tickers)

            n = self.repo.insert_many(all_tickers)
            self.logger.info(f"[insert] inserted: {n}")

            self.logger.info("exchange | asset_type | count")
            for exchange, asset_type, count in self.repo.group_summary():
                self.logger.info(f"{exchange:<8} | {asset_type:<10} | {count}")

            self.logger.info("sample:")
            for row in self.repo.sample():
                self.logger.info("  " + " | ".join(str(v) for v in row))

            self.notifier.send_message(f"[ticker-map] 완료: {n}건 insert")
        except Exception as e:
            self.logger.error(f"[main] failed: {e}")
            self.notifier.send_alert(f"[ticker-map] 실패: {e}")
            raise


def main() -> None:
    App().run()


if __name__ == "__main__":
    main()
