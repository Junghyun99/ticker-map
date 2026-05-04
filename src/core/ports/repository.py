from abc import ABC, abstractmethod
from typing import Iterable

from src.core.entities.ticker import Ticker


class ITickerRepository(ABC):
    @abstractmethod
    def reset_schema(self) -> None: ...
    @abstractmethod
    def insert_many(self, tickers: Iterable[Ticker]) -> int: ...
    @abstractmethod
    def group_summary(self) -> list[tuple]: ...
    @abstractmethod
    def sample(self, limit: int = 5) -> list[tuple]: ...
