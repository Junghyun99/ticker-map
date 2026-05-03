import os
import shutil
import logging
from datetime import datetime, timezone, timedelta
from src.infra.logger import ConverterLogger, KST

def test_logger_creation(tmp_path):
    log_dir = tmp_path / "logs"
    logger = ConverterLogger(log_dir=str(log_dir))
    
    assert os.path.exists(log_dir)
    # 로그 파일명이 오늘 날짜로 생성되었는지 확인
    today = datetime.now(KST).strftime('%Y-%m-%d')
    assert today in logger.log_file

def test_logger_with_run_number(tmp_path):
    log_dir = tmp_path / "logs"
    logger = ConverterLogger(log_dir=str(log_dir), run_number="123")
    assert "_run123" in logger.log_file

def test_logger_output(tmp_path):
    log_dir = tmp_path / "logs"
    logger = ConverterLogger(log_dir=str(log_dir))
    
    logger.info("Test Info Message")
    logger.error("Test Error Message")
    
    with open(logger.log_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Test Info Message" in content
        assert "Test Error Message" in content
        assert "[INFO]" in content
        assert "[ERROR]" in content
