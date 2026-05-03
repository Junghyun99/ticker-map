"""NASDAQ 마스터 다운로더. 해외 공통 동작은 OverseasMasterDownloader 가 담당."""

from src.core.logic.overseas_master import OverseasMasterDownloader


class NasDownloader(OverseasMasterDownloader):
    @property
    def slug(self) -> str: return "nas"
