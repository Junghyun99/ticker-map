from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable

from src.core.schema import Ticker


class ILogger(ABC):
    @abstractmethod
    def debug(self, msg: str) -> None: ...
    @abstractmethod
    def info(self, msg: str) -> None: ...
    @abstractmethod
    def warning(self, msg: str) -> None: ...
    @abstractmethod
    def error(self, msg: str) -> None: ...


class INotifier(ABC):
    @abstractmethod
    def send_message(self, message: str) -> None: ...
    @abstractmethod
    def send_alert(self, message: str) -> None: ...


class ITickerRepository(ABC):
    @abstractmethod
    def reset_schema(self) -> None: ...
    @abstractmethod
    def insert_many(self, tickers: Iterable[Ticker]) -> int: ...
    @abstractmethod
    def group_summary(self) -> list[tuple]: ...
    @abstractmethod
    def sample(self, limit: int = 5) -> list[tuple]: ...


class IArtifactWriter(ABC):
    @abstractmethod
    def write(self, slug: str, tickers: Iterable[Ticker]) -> Path: ...
