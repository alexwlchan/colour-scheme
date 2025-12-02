from typing import TypedDict


class BaseColours(TypedDict):
    background: str
    text: str
    accent_grey: str
    red: str
    green: str
    blue: str
    magenta: str
    yellow: str
    cyan: str
    highlight: str


class Colours(BaseColours):
    background: str
    text: str
    comment: str
    literal: str
    string: str
    name: str
    punctuation: str
    highlight: str


def enrich_colours(c: BaseColours) -> Colours:
    return {
        **c,
        "text": c["text"],
        "comment": c["red"],
        "literal": c["magenta"],
        "string": c["green"],
        "name": c["blue"],
        "punctuation": c["accent_grey"],
    }


class BasePalette(TypedDict):
    id: str
    light: BaseColours
    dark: BaseColours


class Palette(TypedDict):
    light: Colours
    dark: Colours
