#!/usr/bin/env python3
"""
Copy a new set of CSS files from a local checkout of my website, and
create a `palette.json` in the root of the repo.
"""

import glob
from pathlib import Path
import re
import shutil
import subprocess


def get_alexwlchan_net_css(css_name: str) -> tuple[str, str]:
    """
    Get a copy of a CSS file from a local checkout of my website.

    This returns a tuple: the commit ID and CSS text.
    """
    repo_path = Path.home() / "repos/alexwlchan.net"
    css_path = repo_path / "src/_scss" / css_name

    # Get the commit ID of the last change to this file
    output = subprocess.check_output(
        ["git", "rev-list", "-1", "HEAD", "--", str(css_path)],
        text=True,
        cwd=repo_path,
    )
    commit_id = output[:7]

    vendor_path = Path("css") / f"{css_path.stem}.{commit_id}{css_path.suffix}"
    vendor_path.parent.mkdir(exist_ok=True)

    # If we don't have a vendored copy of the file in this repo, delete
    # any previously-vendored copies then copy in the new version.
    if not vendor_path.exists():
        for f in glob.glob("syntax_highlighting.*.scss"):
            Path(f).unlink()

        shutil.copyfile(css_path, vendor_path)

    return commit_id, vendor_path.read_text()


def get_colour_variable(css: str, *, name: str) -> str:
    """
    Extracts a CSS variable from a snippet of CSS.
    """
    m = re.search(f"--{name}:" + r"\s+(?P<colour>#[0-9a-f]{6}([0-9a-f]{2})?);", css)
    assert m is not None
    return m.group("colour")


if __name__ == "__main__":
    variable_id, variable_css = get_alexwlchan_net_css("variables.scss")
    syntax_id, syntax_css = get_alexwlchan_net_css("components/syntax_highlighting.css")

    # Get the default primary colour, which is used for my two shades
    # of red.
    light_red = get_colour_variable(variable_css, name="default-primary-color-light")
    dark_red = get_colour_variable(variable_css, name="default-primary-color-dark")

    print(light_red)
    print(dark_red)
