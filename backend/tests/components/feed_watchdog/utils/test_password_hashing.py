from feed_watchdog.utils.security import hash_password, verify_password


def test_hash_password():
    result = hash_password("qwerty")

    assert result.startswith("$2b$12$")
    assert "qwerty" not in result, "Password should be hashed"


def test_verify_password__correct_password():
    result = verify_password("qwerty", hash_password("qwerty"))

    assert result is True


def test_verify_password__wrong_password():
    result = verify_password("111111", hash_password("qwerty"))

    assert result is False
