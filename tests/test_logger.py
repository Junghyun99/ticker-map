import os
from datetime import datetime

from src.infra.kst_logger import KST, KstLogger


def test_logger_creation(tmp_path):
    log_dir = tmp_path / "logs"
    logger = KstLogger(log_dir=str(log_dir))

    assert os.path.exists(log_dir)
    today = datetime.now(KST).strftime('%Y-%m-%d')
    assert today in logger.log_file


def test_logger_with_run_number(tmp_path):
    log_dir = tmp_path / "logs"
    logger = KstLogger(log_dir=str(log_dir), run_number="123")
    assert "_run123" in logger.log_file


def test_logger_output(tmp_path):
    log_dir = tmp_path / "logs"
    logger = KstLogger(log_dir=str(log_dir))

    logger.info("Test Info Message")
    logger.error("Test Error Message")

    with open(logger.log_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Test Info Message" in content
        assert "Test Error Message" in content
        assert "[INFO]" in content
        assert "[ERROR]" in content
