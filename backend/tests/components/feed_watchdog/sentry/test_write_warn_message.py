from unittest.mock import patch

import pytest

from feed_watchdog.sentry.error_tracking import write_warn_message


class WriterSpy:
    def __init__(self):
        self.messages = []

    def __call__(self, message: str):
        self.messages.append(message)


@pytest.fixture()
def writer_spy():
    return WriterSpy()


@pytest.fixture(autouse=True)
def mock_default_writers(writer_spy):
    with patch(
        "feed_watchdog.sentry.error_tracking.DEFAULT_WRITERS", [writer_spy, writer_spy]
    ):
        yield writer_spy


def test_use_default_writers_if_nothing_is_passed(writer_spy):
    write_warn_message("message")

    assert writer_spy.messages == ["message", "message"]


def test_write_to_passed_writer():
    writer = WriterSpy()
    write_warn_message("message", writer)

    assert writer.messages == ["message"]
