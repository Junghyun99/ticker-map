import io
import zipfile

import pytest

from src.infra.zip_extractor import ZipExtractor


def _make_zip(files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return buf.getvalue()


def test_extract_finds_mst():
    archive = _make_zip({"sample.mst": b"hello-mst"})
    out = ZipExtractor().extract(archive, ".mst")
    assert out == b"hello-mst"


def test_extract_finds_cod_case_insensitive():
    archive = _make_zip({"sample.COD": b"hello-cod"})
    out = ZipExtractor().extract(archive, ".cod")
    assert out == b"hello-cod"


def test_extract_raises_when_suffix_missing():
    archive = _make_zip({"other.txt": b"nope"})
    with pytest.raises(FileNotFoundError):
        ZipExtractor().extract(archive, ".mst")


def test_extract_returns_first_matching_member():
    archive = _make_zip({"a.mst": b"first", "b.mst": b"second"})
    # 첫번째 매칭 멤버를 반환 (zip 멤버 순서는 추가순)
    assert ZipExtractor().extract(archive, ".mst") == b"first"
