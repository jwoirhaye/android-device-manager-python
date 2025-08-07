import pytest

from android_device_manager.utils.validation import is_valid_avd_name


@pytest.mark.parametrize(
    "name,expected",
    [
        ("Pixel_6", True),
        ("A_1-2", True),
        ("avd", True),
        ("a", True),
        ("My-AVD_123", True),
        ("", False),
        ("1start", False),
        ("_underscore", False),
        ("-tiret", False),
        ("with space", False),
        ("foo.bar", False),
        ("foo/bar", False),
        ("foo\\bar", False),
        ("MyAVD!", False),
        (" avd", False),
        ("A" * 256, True),
    ],
)
def test_is_valid_avd_name(name, expected):
    """Test that is_valid_avd_name returns the expected result for various names."""
    assert is_valid_avd_name(name) == expected
