"""KOSPI/KOSDAQ 공통 다운로더 (mst.zip + 고정폭 파싱).

자식이 채울 부분: byte_size, part1/part2 컬럼 + field_specs, normalize_to_schema.
"""

from __future__ import annotations

from abc import abstractmethod
from pathlib import Path

import pandas as pd

from src.core.logic.base import DWS_BASE_URL, MasterDownloader


class KrMasterDownloader(MasterDownloader):
    @property
    @abstractmethod
    def byte_size(self) -> int: ...

    @property
    @abstractmethod
    def part1_columns(self) -> list[str]: ...

    @property
    @abstractmethod
    def field_specs(self) -> list[int]: ...

    @property
    @abstractmethod
    def part2_columns(self) -> list[str]: ...

    def url(self) -> str:
        return f"{DWS_BASE_URL}/{self.slug}_code.mst.zip"

    def expected_raw_columns(self) -> list[str]:
        return list(self.part1_columns) + list(self.part2_columns)

    def _extract_to_dataframe(self, archive: Path, work_dir: Path) -> pd.DataFrame:
        mst_path = self._extract_zip(archive, work_dir, suffix=".mst")

        # part1 은 한글명에 쉼표가 포함될 가능성을 고려해 임시 CSV 대신 메모리 리스트로 보관한다.
        # part2 는 고정폭 포맷이라 파일로 저장 후 pd.read_fwf 로 읽는다.
        part2_path = work_dir / f"{self.slug}_part2.tmp"
        part1_rows: list[list[str]] = []

        with open(mst_path, mode="r", encoding="cp949") as f, \
             open(part2_path, mode="w", encoding="cp949") as wf2:
            for row in f:
                if len(row) <= self.byte_size:
                    continue
                rf1 = row[0:len(row) - self.byte_size]
                part1_rows.append([rf1[0:9].rstrip(), rf1[9:21].rstrip(), rf1[21:].strip()])
                wf2.write(row[-self.byte_size:])

        df1 = pd.DataFrame(part1_rows, columns=self.part1_columns)
        df2 = pd.read_fwf(
            part2_path,
            widths=self.field_specs,
            names=self.part2_columns,
            encoding="cp949",
        )
        return pd.merge(df1, df2, how="outer", left_index=True, right_index=True)
