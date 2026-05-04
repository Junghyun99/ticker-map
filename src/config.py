import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Config:
    def __init__(self) -> None:
        self.SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
        self.LOG_PATH = Path("logs/ci") if os.getenv("GITHUB_ACTIONS") == "true" else Path("logs/local")
        self.DATA_PATH = Path("data")
        self.DB_PATH = Path("tickers.db")
