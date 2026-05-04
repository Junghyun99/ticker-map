from abc import ABC, abstractmethod


class INotifier(ABC):
    @abstractmethod
    def send_message(self, message: str) -> None: ...
    @abstractmethod
    def send_alert(self, message: str) -> None: ...
