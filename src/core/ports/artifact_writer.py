from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable

from src.core.entities.ticker import Ticker


class IArtifactWriter(ABC):
    @abstractmethod
    def write(self, slug: str, tickers: Iterable[Ticker]) -> Path: ...
