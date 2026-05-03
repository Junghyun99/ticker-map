"""마스터 파일 다운로더의 추상 베이스 (템플릿 메서드 패턴).

run() 의 흐름은 모든 거래소가 공유한다:
    1. URL 에서 zip 다운로드
    2. 압축해제 후 raw DataFrame 생성
       - 사전정의 컬럼명 검증 (방어 동작)
    3. raw DataFrame 을 Ticker 도메인 객체 리스트로 정규화
    4. (tempfile 자동 정리)

거래소별로 달라지는 부분만 자식이 정의:
    - url(), slug, expected_raw_columns(), normalize_to_schema(raw)
    - _extract_to_dataframe(archive, work_dir): KR=고정폭, 해외=탭구분

산출물 저장과 DB 적재는 별도 어댑터 책임이다 (이 모듈에서 분리됨).
"""

from __future__ import annotations

import tempfile
import zipfile
from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd
import requests

from src.core.interfaces import ILogger
from src.core.schema import Ticker

DWS_BASE_URL = "https://new.real.download.dws.co.kr/common/master"


class MasterDownloader(ABC):
    """run() 이 템플릿. 자식은 추상 메서드만 채운다."""

    def __init__(self, logger: ILogger) -> None:
        self.logger = logger

    # 자식이 정의 (거래소 정체성)
    @property
    @abstractmethod
    def slug(self) -> str: ...

    @abstractmethod
    def url(self) -> str: ...

    @abstractmethod
    def expected_raw_columns(self) -> list[str]: ...

    @abstractmethod
    def normalize_to_schema(self, raw: pd.DataFrame) -> list[Ticker]: ...

    # 중간 추상(KR vs 해외)이 정의
    @abstractmethod
    def _extract_to_dataframe(self, archive: Path, work_dir: Path) -> pd.DataFrame: ...

    # 템플릿 메서드 — 자식이 override 하지 않음
    def run(self) -> list[Ticker]:
        with tempfile.TemporaryDirectory() as tmp:
            work_dir = Path(tmp)
            archive = self._download(self.url(), work_dir)
            raw = self._extract_to_dataframe(archive, work_dir)
            self._validate_columns(raw)
            tickers = self.normalize_to_schema(raw)
        self.logger.info(f"[normalize] {self.slug} ({len(tickers)} rows)")
        return tickers

    # 공통 구현
    def _download(self, url: str, work_dir: Path) -> Path:
        zip_path = work_dir / Path(url).name
        self.logger.info(f"[download] {url}")
        # DWS 서버의 인증서 체인 이슈로 verify=False 가 불가피하다. 호출 단위로 한정되어
        # 영향 범위는 좁다. 다운로드 데이터는 zip 압축 해제·검증되는 마스터 파일이며,
        # MITM 위험은 인지하고 있다.
        with requests.get(url, stream=True, verify=False, timeout=60) as resp:
            resp.raise_for_status()
            with open(zip_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=64 * 1024):
                    if chunk:
                        f.write(chunk)
        return zip_path

    def _extract_zip(self, archive: Path, work_dir: Path, suffix: str) -> Path:
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(work_dir)
            extracted = [work_dir / name for name in zf.namelist()]
        match = next((p for p in extracted if p.suffix.lower() == suffix.lower()), None)
        if match is None:
            raise FileNotFoundError(f"No {suffix} file found in {archive.name}")
        return match

    def _validate_columns(self, raw: pd.DataFrame) -> None:
        expected = set(self.expected_raw_columns())
        actual = set(raw.columns)
        missing = expected - actual
        if missing:
            raise ValueError(
                f"[{self.slug}] raw 마스터 컬럼 불일치: missing={sorted(missing)}"
            )
