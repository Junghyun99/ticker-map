"""raw 마스터 DataFrame → Ticker 스키마 DataFrame 변환.

main.py 의 load_kospi/kosdaq/nas/nys/ams 5개 함수의 중복을 단일 함수로 통합한다.
거래소별 차이는 ExchangeConfig 로 주입받는다.
"""

import pandas as pd

from src.core.exchanges import ExchangeConfig
from src.core.schema import COLUMNS


def to_ticker_df(raw: pd.DataFrame, cfg: ExchangeConfig) -> pd.DataFrame:
    df = raw.rename(columns=cfg.pre_rename) if cfg.pre_rename else raw
    # alias 는 schema 상 Optional 이라 필수 컬럼만 검사한다 (ticker, asset_type).
    # 해외는 exchange/currency 도 데이터에서 가져오므로 함께 필수.
    required = [cfg.src_ticker_col, cfg.src_asset_type_col]
    if cfg.src_exchange_col:
        required.append(cfg.src_exchange_col)
    if cfg.src_currency_col:
        required.append(cfg.src_currency_col)
    df = df.dropna(subset=required)
    df = df[df[cfg.src_asset_type_col].isin(cfg.asset_type_map)]

    if cfg.ticker_len_filter is not None:
        df = df[df[cfg.src_ticker_col].str.len() == cfg.ticker_len_filter]

    exchange_values = (
        df[cfg.src_exchange_col].values if cfg.src_exchange_col else cfg.code
    )
    currency_values = (
        df[cfg.src_currency_col].values if cfg.src_currency_col else cfg.fixed_currency
    )

    out = pd.DataFrame(
        {
            "ticker": df[cfg.src_ticker_col].values,
            "exchange": exchange_values,
            "alias": df[cfg.src_alias_col].values,
            "asset_type": df[cfg.src_asset_type_col].map(cfg.asset_type_map).values,
            "currency": currency_values,
        }
    )
    return out[list(COLUMNS)]
