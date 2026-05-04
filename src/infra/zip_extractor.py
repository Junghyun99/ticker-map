"""zipfile 기반 IArchiveExtractor 구현. BytesIO 사용으로 디스크 의존 없음."""

from __future__ import annotations

import io
import zipfile

from src.core.ports.archive import IArchiveExtractor


class ZipExtractor(IArchiveExtractor):
    def extract(self, archive: bytes, suffix: str) -> bytes:
        with zipfile.ZipFile(io.BytesIO(archive)) as zf:
            target = next(
                (n for n in zf.namelist() if n.lower().endswith(suffix.lower())),
                None,
            )
            if target is None:
                raise FileNotFoundError(f"No {suffix} file found in archive")
            return zf.read(target)
