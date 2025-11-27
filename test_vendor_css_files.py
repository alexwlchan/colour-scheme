import pytest

from vendor_css_files import get_colour_variable


@pytest.mark.parametrize(
    "css, name, colour",
    [
        # Simplest case
        ("--red: #ff0000;", "red", "#ff0000"),
        # Variable whitespace between varname and hex string
        ("--red:   #ff0000;", "red", "#ff0000"),
        # Alpha channel
        ("--red: #ff0000ff;", "red", "#ff0000ff"),
        # Three-digit hex in source
        ("--grey: #999;", "grey", "#999999"),
    ],
)
def test_get_colour_variable(css: str, name: str, colour: str) -> None:
    """
    Extract colour variables from CSS.
    """
    assert get_colour_variable(css, name=name) == colour
