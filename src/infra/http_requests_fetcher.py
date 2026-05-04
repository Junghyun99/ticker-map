"""requests 기반 IRawSourceFetcher 구현. core 는 이 파일을 import 하지 않는다."""

from __future__ import annotations

import requests

from src.core.ports.raw_source import IRawSourceFetcher


class HttpRequestsFetcher(IRawSourceFetcher):
    def fetch(self, url: str) -> bytes:
        # DWS 서버의 인증서 체인 이슈로 verify=False 가 불가피하다. 호출 단위로 한정되어
        # 영향 범위는 좁다. 다운로드 데이터는 zip 압축 해제·검증되는 마스터 파일이며,
        # MITM 위험은 인지하고 있다.
        with requests.get(url, stream=True, verify=False, timeout=60) as resp:
            resp.raise_for_status()
            return resp.content
