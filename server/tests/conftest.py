import pytest

from processors import settings


@pytest.fixture(autouse=True)
def _mock_handlers_config(monkeypatch):
    monkeypatch.setattr(
        settings,
        "HANDLERS_CONFIG",
        {
            "receivers": {
                "telegram_bot": {
                    "mybot": {
                        "kwargs": {
                            "name": "mybot",
                            "token": (
                                "111111111:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
                            ),
                        }
                    }
                }
            }
        },
    )
