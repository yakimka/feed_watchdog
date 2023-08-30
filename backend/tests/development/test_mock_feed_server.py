import re
import time
from threading import Thread

import httpx
import pytest

from development import mock_feed_server


@pytest.fixture(scope="module")
def server_port():
    return 18765


@pytest.fixture(scope="module")
def server_url(server_port):
    return f"http://localhost:{server_port}"


@pytest.fixture(scope="module", autouse=True)
def _server_process(server_port):
    thread = Thread(
        target=mock_feed_server.main, args=[["", f"--port={server_port}"]], daemon=True
    )
    thread.start()
    time.sleep(1)
    # TODO: add stop server endpoint and call it here


def get_feed(server_url: str, quantity=10):
    params = {"quantity": quantity}
    res = httpx.get(server_url, params=params, timeout=3)
    return res.text


def get_post_ids(text: str) -> list[str]:
    post_ids = []
    for line in text.splitlines():
        if match := re.search(r"<id>(entry.+)</id>", line):
            post_ids.append(match[1])
    return post_ids


def test_get_feed(server_url):
    result = get_feed(server_url)

    assert result.startswith('<?xml version="1.0" encoding="UTF-8"?>')
    assert result.endswith("</feed>")
    assert "<entry>" in result
    assert "</entry>" in result


def test_get_feed_with_one_post(server_url):
    result = get_feed(server_url, quantity=1)

    assert result.count("<entry>") == 1
    assert result.count("</entry>") == 1
    assert "<title>Title of entry #1</title>" in result
    assert '<content type="text">Content of entry #1</content>' in result


def test_posts_has_different_ids(server_url):
    feed_text = get_feed(server_url, quantity=10)
    result = get_post_ids(feed_text)

    assert len(set(result)) == 10


def test_posts_has_different_ids_between_calls(server_url):
    result_first_call = get_post_ids(get_feed(server_url, quantity=1))
    result_second_call = get_post_ids(get_feed(server_url, quantity=1))

    assert all([result_first_call, result_second_call])
    assert result_first_call != result_second_call
