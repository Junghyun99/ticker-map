import os
from pathlib import Path
from src.config import Config

def test_config_default(monkeypatch):
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "http://test.url")
    
    config = Config()
    assert config.SLACK_WEBHOOK_URL == "http://test.url"
    assert config.LOG_PATH == "logs/local"
    assert config.DATA_PATH == Path("data")
    assert config.DB_PATH == Path("tickers.db")

def test_config_github_actions(monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    
    config = Config()
    assert config.LOG_PATH == "logs/ci"
