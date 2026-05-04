from pathlib import Path
from unittest.mock import MagicMock

from src.core.entities.ticker import Ticker
from src.core.sources import ALL_SOURCES, KOSPI, NAS, SourceSpec
from src.core.use_cases.rebuild_ticker_db import RebuildTickerDb


def _build_use_case(
    fetch_returns=b"archive-bytes",
    extract_returns=b"raw-content",
    parse_returns=None,
    normalize_returns=None,
):
    fetcher = MagicMock()
    fetcher.fetch.return_value = fetch_returns

    extractor = MagicMock()
    extractor.extract.return_value = extract_returns

    parser_kr = MagicMock()
    parser_kr.parse.return_value = parse_returns or [{"row": "kr"}]
    parser_overseas = MagicMock()
    parser_overseas.parse.return_value = parse_returns or [{"row": "ov"}]

    fake_ticker_kr = Ticker("005930", "KS", "삼성", "Stock", "KRW")
    fake_ticker_ov = Ticker("AAPL", "NAS", "AAPL", "Stock", "USD")
    norm_kospi = MagicMock(return_value=normalize_returns or [fake_ticker_kr])
    norm_kosdaq = MagicMock(return_value=[])
    norm_overseas = MagicMock(return_value=normalize_returns or [fake_ticker_ov])

    repo = MagicMock()
    repo.insert_many.return_value = 2
    repo.group_summary.return_value = [("KS", "Stock", 1), ("NAS", "Stock", 1)]
    repo.sample.return_value = [("005930", "KS", "삼성", "Stock", "KRW")]

    xlsx_writer = MagicMock()
    xlsx_writer.write.return_value = Path("/tmp/x.xlsx")

    logger = MagicMock()
    notifier = MagicMock()

    use_case = RebuildTickerDb(
        fetcher=fetcher,
        extractor=extractor,
        parsers={"kr_mst": parser_kr, "overseas_cod": parser_overseas},
        normalizers={"kospi": norm_kospi, "kosdaq": norm_kosdaq, "overseas": norm_overseas},
        repo=repo,
        xlsx_writer=xlsx_writer,
        logger=logger,
        notifier=notifier,
    )
    return use_case, {
        "fetcher": fetcher,
        "extractor": extractor,
        "parser_kr": parser_kr,
        "parser_overseas": parser_overseas,
        "norm_kospi": norm_kospi,
        "norm_kosdaq": norm_kosdaq,
        "norm_overseas": norm_overseas,
        "repo": repo,
        "xlsx_writer": xlsx_writer,
        "logger": logger,
    }


def test_execute_resets_schema_first():
    uc, mocks = _build_use_case()
    uc.execute([KOSPI])
    mocks["repo"].reset_schema.assert_called_once()


def test_execute_calls_pipeline_in_order_for_each_source():
    uc, mocks = _build_use_case()
    uc.execute([KOSPI])

    mocks["fetcher"].fetch.assert_called_once_with(KOSPI.url)
    mocks["extractor"].extract.assert_called_once_with(b"archive-bytes", ".mst")
    mocks["parser_kr"].parse.assert_called_once_with(b"raw-content", "kospi")
    mocks["norm_kospi"].assert_called_once_with([{"row": "kr"}])
    mocks["xlsx_writer"].write.assert_called_once()
    args, _ = mocks["xlsx_writer"].write.call_args
    assert args[0] == "kospi"


def test_execute_routes_overseas_to_overseas_parser_and_normalizer():
    uc, mocks = _build_use_case()
    uc.execute([NAS])

    mocks["parser_overseas"].parse.assert_called_once_with(b"raw-content", "nas")
    mocks["norm_overseas"].assert_called_once()
    mocks["parser_kr"].parse.assert_not_called()
    mocks["norm_kospi"].assert_not_called()


def test_execute_inserts_all_collected_tickers():
    uc, mocks = _build_use_case()
    n = uc.execute([KOSPI, NAS])

    # insert_many 가 각 source 의 ticker 를 누적해 호출되어야 함
    mocks["repo"].insert_many.assert_called_once()
    inserted_arg = list(mocks["repo"].insert_many.call_args[0][0])
    assert len(inserted_arg) == 2
    assert n == 2  # repo.insert_many 의 반환값


def test_execute_iterates_all_sources():
    uc, mocks = _build_use_case()
    uc.execute(ALL_SOURCES)

    # 5개 거래소 모두 fetch 됨
    assert mocks["fetcher"].fetch.call_count == 5
    assert mocks["xlsx_writer"].write.call_count == 5


def test_execute_handles_unknown_parser_kind():
    uc, mocks = _build_use_case()
    bad_source = SourceSpec(
        slug="x", url="http://x", archive_suffix=".x",
        parser_kind="missing", normalizer_kind="kospi",
    )
    try:
        uc.execute([bad_source])
        assert False, "KeyError 가 발생해야 한다"
    except KeyError:
        pass
