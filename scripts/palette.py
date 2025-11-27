from typing import TypedDict


class Colours(TypedDict):
    red: str
    green: str
    blue: str
    magenta: str
    yellow: str
    highlight: str


class Palette(TypedDict):
    id: str
    light: Colours
    dark: Colours
