"""5거래소 마스터 → 정규화 → DB/xlsx 적재 흐름을 지휘하는 유스케이스.

포트만 import. 외부 라이브러리·OS 의존 없음.
"""

from __future__ import annotations

from typing import Iterable, Mapping

from src.core.entities.ticker import Ticker
from src.core.ports.archive import IArchiveExtractor
from src.core.ports.artifact_writer import IArtifactWriter
from src.core.ports.logger import ILogger
from src.core.ports.normalizer import Normalizer
from src.core.ports.notifier import INotifier
from src.core.ports.raw_parser import IRawParser
from src.core.ports.raw_source import IRawSourceFetcher
from src.core.ports.repository import ITickerRepository
from src.core.sources import SourceSpec


class RebuildTickerDb:
    def __init__(
        self,
        fetcher: IRawSourceFetcher,
        extractor: IArchiveExtractor,
        parsers: Mapping[str, IRawParser],
        normalizers: Mapping[str, Normalizer],
        repo: ITickerRepository,
        xlsx_writer: IArtifactWriter,
        logger: ILogger,
        notifier: INotifier,
    ) -> None:
        self.fetcher = fetcher
        self.extractor = extractor
        self.parsers = parsers
        self.normalizers = normalizers
        self.repo = repo
        self.xlsx_writer = xlsx_writer
        self.logger = logger
        self.notifier = notifier

    def execute(self, sources: Iterable[SourceSpec]) -> int:
        all_tickers: list[Ticker] = []
        for s in sources:
            self.logger.info(f"[download] {s.url}")
            archive = self.fetcher.fetch(s.url)
            content = self.extractor.extract(archive, s.archive_suffix)
            rows = self.parsers[s.parser_kind].parse(content, s.slug)
            tickers = self.normalizers[s.normalizer_kind](rows)
            self.logger.info(f"[normalize] {s.slug} ({len(tickers)} rows)")
            self.xlsx_writer.write(s.slug, tickers)
            all_tickers.extend(tickers)

        self.repo.reset_schema()
        n = self.repo.insert_many(all_tickers)
        self.logger.info(f"[insert] inserted: {n}")

        self.logger.info("exchange | asset_type | count")
        for exchange, asset_type, count in self.repo.group_summary():
            self.logger.info(f"{exchange:<8} | {asset_type:<10} | {count}")

        self.logger.info("sample:")
        for row in self.repo.sample():
            self.logger.info("  " + " | ".join(str(v) for v in row))

        return n
