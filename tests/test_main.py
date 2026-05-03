import os
from unittest.mock import MagicMock, patch
import pytest
from src.main import App
from src.core.schema import Ticker

def test_app_init(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_RUN_NUMBER", "1")
    
    db_path = tmp_path / "tickers.db"
    log_path = tmp_path / "logs"
    data_path = tmp_path / "data"
    
    # Config 멤버들을 패치하거나 monkeypatch로 환경변수 조절
    monkeypatch.setattr("src.config.Config.__init__", lambda self: None)
    
    with patch("src.main.Config") as MockConfig:
        MockConfig.return_value.DB_PATH = db_path
        MockConfig.return_value.LOG_PATH = str(log_path)
        MockConfig.return_value.DATA_PATH = data_path
        MockConfig.return_value.SLACK_WEBHOOK_URL = ""
        
        app = App()
        assert app.repo.db_path == db_path
        assert len(app.downloaders) == 5

def test_app_run_success(tmp_path, monkeypatch):
    db_path = tmp_path / "tickers.db"
    log_path = tmp_path / "logs"
    data_path = tmp_path / "data"
    
    with patch("src.main.Config") as MockConfig:
        MockConfig.return_value.DB_PATH = db_path
        MockConfig.return_value.LOG_PATH = str(log_path)
        MockConfig.return_value.DATA_PATH = data_path
        MockConfig.return_value.SLACK_WEBHOOK_URL = ""
        
        app = App()
        
        # downloader.run() 이 가짜 데이터를 반환하도록 패치
        for i, d in enumerate(app.downloaders):
            fake_ticker = Ticker(f"TICK{i}", "EX", "NAME", "Stock", "CUR")
            d.run = MagicMock(return_value=[fake_ticker])
            
        app.run()
        
        # DB에 데이터가 들어갔는지 확인
        summary = app.repo.group_summary()
        assert len(summary) > 0
        assert sum(s[2] for s in summary) == len(app.downloaders)

def test_app_run_failure(tmp_path, monkeypatch):
    db_path = tmp_path / "tickers.db"
    log_path = tmp_path / "logs"
    data_path = tmp_path / "data"
    
    with patch("src.main.Config") as MockConfig:
        MockConfig.return_value.DB_PATH = db_path
        MockConfig.return_value.LOG_PATH = str(log_path)
        MockConfig.return_value.DATA_PATH = data_path
        MockConfig.return_value.SLACK_WEBHOOK_URL = ""
        
        app = App()
        
        # 하나라도 실패하면 전체 실패
        app.downloaders[0].run = MagicMock(side_effect=Exception("Download failed"))
        
        with pytest.raises(Exception, match="Download failed"):
            app.run()
        
        # 실패 메시지가 로그에 남았는지 확인 (logger는 Mock이 아니므로 파일 확인 가능)
        # 하지만 여기서는 notifier가 호출되었는지만 봐도 됨
        assert app.notifier.webhook_url == "" # MockNotifier가 아님
