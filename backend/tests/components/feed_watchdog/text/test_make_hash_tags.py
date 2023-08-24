import pytest

from feed_watchdog.text import make_hash_tags


@pytest.mark.parametrize(
    "tags, expected",
    [
        pytest.param(
            ["Hello", "world"], ["#hello", "#world"], id="english_only"
        ),
        pytest.param(
            ["Hello123", "world456"], ["#hello123", "#world456"], id="numbers"
        ),
        pytest.param(
            ["Hello!", "world@@"],
            ["#hello_", "#world_"],
            id="special_characters",
        ),
        pytest.param(
            ["Hello!!", "world@@@"],
            ["#hello_", "#world_"],
            id="multiple_special_to_single_underscore",
        ),
        pytest.param(
            ["Привет", "Мир"], ["#привет", "#мир"], id="non_english_chars"
        ),
        pytest.param(
            ["Привет123!@", "Мир456"],
            ["#привет123_", "#мир456"],
            id="combined_chars",
        ),
        pytest.param([], [], id="empty_input"),
        pytest.param(["", ""], ["#", "#"], id="empty_strings"),
        pytest.param(["!!", "@@"], ["#_", "#_"], id="only_special_chars"),
    ],
)
def test_make_hash_tags(tags, expected):
    result = make_hash_tags(tags)

    assert result == expected
