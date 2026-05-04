from abc import ABC, abstractmethod


class IRawSourceFetcher(ABC):
    @abstractmethod
    def fetch(self, url: str) -> bytes: ...
