#!/usr/bin/env python3
"""
Copy a new set of CSS files from a local checkout of my website, and
create a `palette.json` in the root of the repo.
"""

import glob
import json
from pathlib import Path
import re
import shutil
import subprocess

from palette import BaseColours, BasePalette


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
        for f in glob.glob(f"css/{css_path.stem}.*"):
            Path(f).unlink()

        shutil.copyfile(css_path, vendor_path)

    return commit_id, vendor_path.read_text()


def get_colour_variable(css: str, *, name: str) -> str:
    """
    Extracts a CSS variable from a snippet of CSS.
    """
    # Example matches:
    #
    #     --red: #ff0000;
    #     --red:   #ff0000;
    #     --red: #ff0000ff;
    #
    m = re.search(f"{name}:" + r"\s*(?P<colour>#[0-9a-f]+);", css)

    if m is None:
        raise ValueError(f"cannot find variable --{name} in CSS")

    c = m.group("colour")

    # 6- or 8-digit hex colour
    if len(c) == 7 or len(c) == 9:
        return c

    # 3-digit hex colour, so double each digit
    if len(c) == 4:
        return f"#{c[1] * 2}{c[2] * 2}{c[3] * 2}"

    raise ValueError(f"unrecognised hex string: {c}")


if __name__ == "__main__":
    variable_id, variable_css = get_alexwlchan_net_css("variables.scss")
    syntax_id, syntax_css = get_alexwlchan_net_css("components/syntax_highlighting.css")

    light_colours: BaseColours = {
        "background": get_colour_variable(
            variable_css, name="--background-color-light"
        ),
        "text": get_colour_variable(variable_css, name="--body-text-light"),
        "accent_grey": get_colour_variable(variable_css, name="--accent-grey-light"),
        "red": get_colour_variable(variable_css, name="--default-primary-color-light"),
        "green": get_colour_variable(syntax_css, name="--green"),
        "blue": get_colour_variable(syntax_css, name="--blue"),
        "magenta": get_colour_variable(syntax_css, name="--magenta"),
        "yellow": get_colour_variable(syntax_css, name="--yellow"),
        "highlight": get_colour_variable(syntax_css, name="--highlight"),
    }

    # Get the first block of dark theme colours from the syntax highlighting
    # CSS. This is a bit crude, but it works for now.
    _, dark_syntax_css = syntax_css.split("@media (prefers-color-scheme: dark) {")
    dark_colours: BaseColours = {
        "background": get_colour_variable(variable_css, name="--background-color-dark"),
        "text": get_colour_variable(variable_css, name="--body-text-dark"),
        "accent_grey": get_colour_variable(variable_css, name="--accent-grey-dark"),
        "red": get_colour_variable(variable_css, name="--default-primary-color-dark"),
        "green": get_colour_variable(dark_syntax_css, name="--green"),
        "blue": get_colour_variable(dark_syntax_css, name="--blue"),
        "magenta": get_colour_variable(dark_syntax_css, name="--magenta"),
        "yellow": get_colour_variable(dark_syntax_css, name="--yellow"),
        "highlight": get_colour_variable(dark_syntax_css, name="--highlight"),
    }

    # When I do <mark> highlights on my blog, I keep the text black in
    # dark mode, but for my themes, use a more muted yellow.
    if dark_colours["highlight"] == "#fffc42cc":
        dark_colours["highlight"] = "#fffc4244"
    else:
        raise ValueError(f"Unrecognised dark colour: {dark_colours['highlight']}")

    palette: BasePalette = {
        "id": f"{variable_id}-{syntax_id}",
        "light": light_colours,
        "dark": dark_colours,
    }

    with open("palette.json", "w") as out_file:
        out_file.write(json.dumps(palette, indent=2))

    print(f"Written palette {palette['id']} to palette.json")
