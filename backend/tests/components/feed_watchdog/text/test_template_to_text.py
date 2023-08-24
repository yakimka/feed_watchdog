from typing import Any

import pytest

from feed_watchdog.text import template_to_text


@pytest.mark.parametrize(
    "template_string, kwargs, expected",
    [
        pytest.param(
            "Hello, $name!",
            {"name": "Alice"},
            "Hello, Alice!",
            id="basic_substitution",
        ),
        pytest.param(
            "Hello, $name!",
            {},
            "Hello, $name!",
            id="missing_key_no_substitution",
        ),
        pytest.param(
            "Prices: $apple, $orange.",
            {"apple": "0.5$", "orange": "0.6$"},
            "Prices: 0.5$, 0.6$.",
            id="multiple_substitutions",
        ),
        pytest.param(
            "$x + $x = $y",
            {"x": "1", "y": "2"},
            "1 + 1 = 2",
            id="math_expression",
        ),
        pytest.param(
            "Hello, ${name}!",
            {"name": "Alice"},
            "Hello, Alice!",
            id="curly_braces_substitution",
        ),
        pytest.param(
            "Hi, $name1 and $name2!",
            {"name1": "Alice", "name2": "Bob"},
            "Hi, Alice and Bob!",
            id="multiple_keys",
        ),
        pytest.param("", {"name": "Alice"}, "", id="empty_template"),
    ],
)
def test_template_to_text(template_string: str, kwargs: Any, expected: str):
    result = template_to_text(template_string, **kwargs)

    assert result == expected
