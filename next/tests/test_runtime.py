import sys


def test_interpreter_is_at_least_3_14_7() -> None:
    assert sys.version_info >= (3, 14, 7)
