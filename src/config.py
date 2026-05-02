import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    def __init__(self) -> None:
        self.SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
        self.LOG_PATH = "logs/ci" if os.getenv("GITHUB_ACTIONS") == "true" else "logs/local"
        self.DATA_PATH: Path = BASE_DIR / "data"
        self.DB_PATH: Path = BASE_DIR / "tickers.db"
