from unittest.mock import patch

import pytest

from feed_watchdog.sentry.setup import setup_fastapi, setup_logging


@pytest.fixture()
def mock_sentry_init():
    with patch("feed_watchdog.sentry.setup.sentry_sdk.init") as mock_method:
        yield mock_method


def test_setup_logging_with_dsn(mock_sentry_init, caplog):
    setup_logging("test_dsn")

    assert mock_sentry_init.call_count == 1
    assert not caplog.records


def test_setup_fastapi_with_dsn(mock_sentry_init, caplog):
    setup_fastapi("test_dsn")

    assert mock_sentry_init.call_count == 1
    assert not caplog.records


@pytest.mark.parametrize(
    "dsn",
    [
        pytest.param(None, id="no_dsn"),
        pytest.param("", id="empty_dsn"),
    ],
)
def test_setup_logging_without_dsn(dsn: str | None, mock_sentry_init, caplog):
    setup_logging(dsn)

    assert mock_sentry_init.call_count == 0
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "WARNING"
    assert caplog.records[0].message == "Sentry DSN is not set"


@pytest.mark.parametrize(
    "dsn",
    [
        pytest.param(None, id="no_dsn"),
        pytest.param("", id="empty_dsn"),
    ],
)
def test_setup_fastapi_without_dsn(dsn: str | None, mock_sentry_init, caplog):
    setup_fastapi(dsn)

    assert mock_sentry_init.call_count == 0
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "WARNING"
    assert caplog.records[0].message == "Sentry DSN is not set"
