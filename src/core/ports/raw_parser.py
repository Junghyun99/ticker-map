from abc import ABC, abstractmethod


class IRawParser(ABC):
    @abstractmethod
    def parse(self, content: bytes, slug: str) -> list[dict]: ...
