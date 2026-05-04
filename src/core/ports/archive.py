from abc import ABC, abstractmethod


class IArchiveExtractor(ABC):
    @abstractmethod
    def extract(self, archive: bytes, suffix: str) -> bytes:
        """지정한 확장자의 첫 멤버 파일 내용을 bytes 로 반환."""
