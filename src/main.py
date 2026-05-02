"""data/*_code.xlsx 5개를 읽어 README 스키마에 맞춘 tickers.db(SQLite) 를 생성한다.

스키마: ticker(PK), exchange, alias, asset_type, currency
거래소별 변환 규칙은 src/core/exchanges.py 의 ExchangeConfig 로 표현된다.
"""

import os
import sqlite3
from pathlib import Path

import pandas as pd

from src.config import Config
from src.core.exchanges import EXCHANGES, ExchangeConfig
from src.core.schema import (
    COLUMNS,
    CREATE_TABLE_SQL,
    DROP_TABLE_SQL,
    INSERT_SQL,
    TABLE_NAME,
)
from src.core.transformer import to_ticker_df
from src.infra.logger import ConverterLogger
from src.infra.notifier import SlackNotifier


def load_exchange(cfg: ExchangeConfig, data_dir: Path) -> pd.DataFrame:
    raw = pd.read_excel(
        data_dir / cfg.xlsx_filename,
        usecols=cfg.read_usecols,
        dtype=cfg.read_dtype,
    )
    return to_ticker_df(raw, cfg)


def init_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(DROP_TABLE_SQL)
    cur.execute(CREATE_TABLE_SQL)
    conn.commit()
    return conn


def bulk_insert(conn: sqlite3.Connection, df: pd.DataFrame) -> int:
    cur = conn.cursor()
    cur.executemany(INSERT_SQL, df.itertuples(index=False, name=None))
    conn.commit()
    return len(df)


def main() -> None:
    config = Config()
    run_number = os.getenv("GITHUB_RUN_NUMBER")
    logger = ConverterLogger(log_dir=config.LOG_PATH, run_number=run_number)
    slack = SlackNotifier(webhook_url=config.SLACK_WEBHOOK_URL, logger=logger)

    frames = [load_exchange(cfg, config.DATA_PATH) for cfg in EXCHANGES]
    counts = ", ".join(f"{cfg.slug}: {len(df)}" for cfg, df in zip(EXCHANGES, frames))
    logger.info(f"[load] {counts}")
    df = pd.concat(frames, ignore_index=True)

    conn = init_db(config.DB_PATH)
    try:
        n = bulk_insert(conn, df)
        logger.info(f"[insert] inserted: {n}")

        cur = conn.cursor()
        logger.info("exchange | asset_type | count")
        for exchange, asset_type, count in cur.execute(
            f"SELECT exchange, asset_type, COUNT(*) FROM {TABLE_NAME} "
            "GROUP BY exchange, asset_type ORDER BY exchange, asset_type;"
        ):
            logger.info(f"{exchange:<8} | {asset_type:<10} | {count}")

        logger.info("sample:")
        for row in cur.execute(f"SELECT * FROM {TABLE_NAME} LIMIT 5;"):
            logger.info("  " + " | ".join(str(v) for v in row))

        slack.send_message(f"[ticker-map] 완료: {n}건 insert")
    except Exception as e:
        logger.error(f"[main] failed: {e}")
        slack.send_alert(f"[ticker-map] 실패: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
