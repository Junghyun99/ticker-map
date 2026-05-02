"""KOSPI/KOSDAQ/해외 마스터 파일 공통 다운로더.

kospi_code.py, kosdaq_code.py 의 fixed-width 파싱 흐름과 overseas_code.py 의
tab-separated 파싱 흐름을 각각 단일 함수로 통합한다. 거래소별로 달라지는 부분은
인자로 주입받는다.

기존 동작과의 차이:
- os.chdir 미사용 (절대경로 인자만 사용)
- 임시파일은 tempfile.TemporaryDirectory 로 자동 정리
- urllib + ssl 글로벌 mutation → requests + verify=False per-call
- print → ILogger 주입 (logger=None 이면 무출력)
"""

from __future__ import annotations

import tempfile
import zipfile
from pathlib import Path
from typing import Optional

import pandas as pd
import requests

from src.core.interfaces import ILogger

DWS_BASE_URL = "https://new.real.download.dws.co.kr/common/master"


def _log(logger: Optional[ILogger], msg: str) -> None:
    if logger is not None:
        logger.info(msg)


def _download_and_extract(url: str, work_dir: Path, logger: Optional[ILogger]) -> list[Path]:
    """URL 의 zip 을 work_dir 에 다운로드/해제하고 풀린 파일 경로 리스트 반환."""
    zip_path = work_dir / Path(url).name
    _log(logger, f"[download] {url}")
    # DWS 서버의 인증서 체인 이슈로 verify=False 가 불가피하다. 기존 코드의 글로벌
    # ssl._create_unverified_context 보다는 호출 단위로 한정되어 영향 범위가 좁다.
    # MITM 위험은 인지하고 있으며, 다운로드 데이터는 zip 압축 해제·검증되는 마스터 파일이다.
    with requests.get(url, stream=True, verify=False, timeout=60) as resp:
        resp.raise_for_status()
        with open(zip_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=64 * 1024):
                if chunk:
                    f.write(chunk)

    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(work_dir)
        extracted = [work_dir / name for name in zf.namelist()]
    return extracted


def download_kr_master(
    slug: str,
    byte_size: int,
    part1_columns: list[str],
    field_specs: list[int],
    part2_columns: list[str],
    data_dir: Path,
    logger: Optional[ILogger] = None,
) -> pd.DataFrame:
    """KOSPI/KOSDAQ .mst.zip 다운로드 → 압축해제 → fixed-width 파싱 → xlsx 저장.

    byte_size: KOSPI=228, KOSDAQ=222 (한 행에서 part2 가 차지하는 바이트 수)
    """
    data_dir.mkdir(parents=True, exist_ok=True)
    url = f"{DWS_BASE_URL}/{slug}_code.mst.zip"

    with tempfile.TemporaryDirectory() as tmp:
        work_dir = Path(tmp)
        extracted = _download_and_extract(url, work_dir, logger)
        mst_path = next((p for p in extracted if p.suffix == ".mst"), None)
        if mst_path is None:
            raise FileNotFoundError(f"No .mst file found in {url}")

        # part1 은 한글명에 쉼표가 포함될 가능성을 고려해 임시 CSV 대신 메모리 리스트로 보관한다.
        # part2 는 고정폭 포맷이므로 파일로 저장 후 pd.read_fwf 로 읽는다.
        part2_path = work_dir / f"{slug}_part2.tmp"
        part1_rows: list[list[str]] = []

        with open(mst_path, mode="r", encoding="cp949") as f, \
             open(part2_path, mode="w", encoding="cp949") as wf2:
            for row in f:
                if len(row) <= byte_size:
                    continue
                rf1 = row[0:len(row) - byte_size]
                part1_rows.append([rf1[0:9].rstrip(), rf1[9:21].rstrip(), rf1[21:].strip()])
                wf2.write(row[-byte_size:])

        df1 = pd.DataFrame(part1_rows, columns=part1_columns)
        df2 = pd.read_fwf(part2_path, widths=field_specs, names=part2_columns, encoding="cp949")
        df = pd.merge(df1, df2, how="outer", left_index=True, right_index=True)

    xlsx_path = data_dir / f"{slug}_code.xlsx"
    df.to_excel(xlsx_path, index=False)
    _log(logger, f"[excel] {xlsx_path} ({len(df)} rows)")
    return df


def download_overseas_master(
    slug: str,
    columns: list[str],
    data_dir: Path,
    logger: Optional[ILogger] = None,
) -> pd.DataFrame:
    """해외 {slug}mst.cod.zip 다운로드 → 압축해제 → tab-separated 파싱 → xlsx 저장.

    columns: 원본 .cod 파일의 컬럼 헤더 (24개). 컬럼 수 불일치 시 ValueError.
    """
    data_dir.mkdir(parents=True, exist_ok=True)
    url = f"{DWS_BASE_URL}/{slug}mst.cod.zip"

    with tempfile.TemporaryDirectory() as tmp:
        work_dir = Path(tmp)
        extracted = _download_and_extract(url, work_dir, logger)
        cod_path = next((p for p in extracted if p.suffix == ".cod"), None)
        if cod_path is None:
            raise FileNotFoundError(f"No .cod file found in {url}")

        df = pd.read_table(cod_path, sep="\t", encoding="cp949")
        if len(df.columns) != len(columns):
            raise ValueError(
                f"[{slug}] column count mismatch: expected {len(columns)}, got {len(df.columns)}"
            )
        df.columns = columns

    xlsx_path = data_dir / f"{slug}_code.xlsx"
    df.to_excel(xlsx_path, index=False)
    _log(logger, f"[excel] {xlsx_path} ({len(df)} rows)")
    return df
