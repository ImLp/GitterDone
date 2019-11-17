"""Unit Test Suite targetting StringUtilities.py."""
from .. import StringUtilities


def test_normalize_string():
    """Test Normalize String."""
    expected = "abc"
    actual = StringUtilities.normalize_string(" abc      ")
    assert expected == actual


def test_normalize_wildcards():
    """This test should Fail."""
    expect = "abc"
    actual = StringUtilities.normalize_string("abc*", remove_wildcards=True)
    assert expect == actual
