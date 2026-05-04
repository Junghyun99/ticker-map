"""거래소 정의를 데이터로 표현. core 는 거래소 추가/변경 시 이 파일만 본다."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

DWS_BASE_URL = "https://new.real.download.dws.co.kr/common/master"

ArchiveSuffix = Literal[".mst", ".cod"]
ParserKind = Literal["kr_mst", "overseas_cod"]
NormalizerKind = Literal["kospi", "kosdaq", "overseas"]


@dataclass(frozen=True)
class SourceSpec:
    slug: str
    url: str
    archive_suffix: ArchiveSuffix
    parser_kind: ParserKind
    normalizer_kind: NormalizerKind


KOSPI = SourceSpec(
    slug="kospi",
    url=f"{DWS_BASE_URL}/kospi_code.mst.zip",
    archive_suffix=".mst",
    parser_kind="kr_mst",
    normalizer_kind="kospi",
)
KOSDAQ = SourceSpec(
    slug="kosdaq",
    url=f"{DWS_BASE_URL}/kosdaq_code.mst.zip",
    archive_suffix=".mst",
    parser_kind="kr_mst",
    normalizer_kind="kosdaq",
)
NAS = SourceSpec(
    slug="nas",
    url=f"{DWS_BASE_URL}/nasmst.cod.zip",
    archive_suffix=".cod",
    parser_kind="overseas_cod",
    normalizer_kind="overseas",
)
NYS = SourceSpec(
    slug="nys",
    url=f"{DWS_BASE_URL}/nysmst.cod.zip",
    archive_suffix=".cod",
    parser_kind="overseas_cod",
    normalizer_kind="overseas",
)
AMS = SourceSpec(
    slug="ams",
    url=f"{DWS_BASE_URL}/amsmst.cod.zip",
    archive_suffix=".cod",
    parser_kind="overseas_cod",
    normalizer_kind="overseas",
)

ALL_SOURCES: list[SourceSpec] = [KOSPI, KOSDAQ, NAS, NYS, AMS]
