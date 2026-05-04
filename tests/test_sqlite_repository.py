from pathlib import Path
from src.core.entities.ticker import Ticker
from src.infra.sqlite_repository import SqliteTickerRepository

def test_sqlite_repo_flow(tmp_path):
    db_path = tmp_path / "test_tickers.db"
    repo = SqliteTickerRepository(db_path)
    
    # 1. 초기화
    repo.reset_schema()
    
    # 2. 삽입
    tickers = [
        Ticker("005930", "KS", "삼성전자", "Stock", "KRW"),
        Ticker("000660", "KS", "SK하이닉스", "Stock", "KRW"),
        Ticker("AAPL", "NAS", "AAPL", "Stock", "USD")
    ]
    count = repo.insert_many(tickers)
    assert count == 3
    
    # 3. 요약
    summary = repo.group_summary()
    # KS Stock 2, NAS Stock 1
    assert ("KS", "Stock", 2) in summary
    assert ("NAS", "Stock", 1) in summary
    
    # 4. 샘플
    samples = repo.sample(limit=1)
    assert len(samples) == 1
    assert samples[0][0] in ["005930", "000660", "AAPL"]
