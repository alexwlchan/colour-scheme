#!/usr/bin/env python3

from datetime import datetime, timezone
import io
import json
from pathlib import Path
import plistlib
import textwrap
from typing import TypedDict

from jinja2 import Template

from palette import Colours, Palette, enrich_colours


def get_palette() -> tuple[str, Palette]:
    """
    Read the palette colours from `palette.json`.
    """
    with open("palette.json") as in_file:
        data = json.load(in_file)

    return data["id"], {
        "light": enrich_colours(data["light"]),
        "dark": enrich_colours(data["dark"]),
    }


def generate_textmate_theme(colours: Colours, palette_id: str) -> str:
    """
    Generate a TextMate theme based on my palette.
    """
    template = Template("""
    // Generated from palette {{palette_id}} at {{now}}
    // See https://github.com/alexwlchan/colour-scheme
    {\tsettings = (
    \t\t{%- for block in settings %}
    \t\t{\t{% for k, v in block.items() -%}
    \t\t\t\t{{ k }} = {% if v is mapping %}{
    \t\t\t\t{%- for kk, vv in v.items() %}
    \t\t\t\t{{ kk }} = '{{ vv }}';{% endfor %}
    \t\t\t};{% else %}'{{ v }}';
    \t\t\t{% endif %}{% endfor %}
    \t\t},{% endfor %}
    \t);
    }
    """)

    settings = [
        {
            "settings": {
                "foreground": colours["text"],
                "background": colours["background"],
                "caret": colours["text"],
                "invisibles": colours["punctuation"],
                "selection": colours["highlight"],
                "lineHighlight": colours["highlight"],
            }
        },
        {
            "name": "Text base",
            "scope": "text",
            "settings": {
                "foreground": colours["text"],
                "background": colours["background"],
            },
        },
        {
            "name": "Source base",
            "scope": "source - source source",
            "settings": {
                "foreground": colours["text"],
                "background": colours["background"],
            },
        },
    ]

    for name, scope in [
        ("Text base", "text"),
        ("Source base", "source - source source"),
        ("Embedded source (text)", "text meta.embedded"),
        ("Embedded source (source)", "source meta.embedded"),
    ]:
        settings.append(
            {
                "name": name,
                "scope": scope,
                "settings": {
                    "foreground": colours["text"],
                    "background": colours["background"],
                },
            }
        )

    for scope, colour in [
        ("comment", colours["comment"]),
        ("source comment.block", colours["comment"]),
        ("constant", colours["literal"]),
        ("entity.name", colours["name"]),
        ("variable", colours["name"]),
        ("meta.class.ruby", colours["name"]),
        ("keyword.control.class.ruby", colours["text"]),
        ("meta.identifier.python", colours["name"]),
        ("markup.heading.1.markdown", colours["name"]),
        ("markup.heading.2.markdown", colours["name"]),
        ("markup.heading.3.markdown", colours["name"]),
        ("markup.heading.4.markdown", colours["name"]),
        ("markup.heading.5.markdown", colours["name"]),
        ("markup.heading.6.markdown", colours["name"]),
        ("string", colours["string"]),
        ("string constant.character.escape", colours["string"]),
        ("string.interpolated", colours["string"]),
        ("string.literal", colours["string"]),
        ("string.interpolated constant.character.escape", colours["string"]),
    ]:
        settings.append(
            {"name": scope, "scope": scope, "settings": {"foreground": colour}}
        )

    out = template.render(
        settings=settings,
        palette_id=palette_id,
        now=datetime.now(tz=timezone.utc).isoformat(),
    )
    out = textwrap.dedent(out)
    out = out.strip()
    return out


iTermColour = TypedDict(
    "iTermColour",
    {
        "Red Component": float,
        "Gren Component": float,
        "Blue Component": float,
        "Alpha Component": float,
        "Color Space": str,
    },
)


def to_iterm2_colour(hex_string) -> iTermColour:
    r_255 = int(hex_string[1:3], 16)
    g_255 = int(hex_string[3:5], 16)
    b_255 = int(hex_string[5:7], 16)

    return {
        "Red Component": r_255 / 255,
        "Green Component": g_255 / 255,
        "Blue Component": b_255 / 255,
        "Alpha Component": 1.0,
        "Color Space": "SRGB",
    }


def generate_iterm2_theme(palette: Palette) -> bytes:
    """
    Generate an iTerm 2 theme based on my palette.
    """
    out = {
        "Background Color (Dark)": to_iterm2_colour(palette["dark"]["background"]),
        "Background Color (Light)": to_iterm2_colour(palette["light"]["background"]),
        "Foreground Color (Dark)": to_iterm2_colour(palette["dark"]["text"]),
        "Foreground Color (Light)": to_iterm2_colour(palette["light"]["text"]),
        "Link Color (Dark)": to_iterm2_colour(palette["dark"]["blue"]),
        "Link Color (Light)": to_iterm2_colour(palette["light"]["blue"]),
        "Ansi 0 Color (Dark)": to_iterm2_colour(palette["dark"]["text"]),
        "Ansi 0 Color (Light)": to_iterm2_colour(palette["light"]["text"]),
        "Ansi 1 Color (Dark)": to_iterm2_colour(palette["dark"]["red"]),
        "Ansi 1 Color (Light)": to_iterm2_colour(palette["light"]["red"]),
        "Ansi 2 Color (Dark)": to_iterm2_colour(palette["dark"]["green"]),
        "Ansi 2 Color (Light)": to_iterm2_colour(palette["light"]["green"]),
        "Ansi 3 Color (Dark)": to_iterm2_colour(palette["dark"]["yellow"]),
        "Ansi 3 Color (Light)": to_iterm2_colour(palette["light"]["yellow"]),
        "Ansi 4 Color (Dark)": to_iterm2_colour(palette["dark"]["blue"]),
        "Ansi 4 Color (Light)": to_iterm2_colour(palette["light"]["blue"]),
        "Ansi 5 Color (Dark)": to_iterm2_colour(palette["dark"]["magenta"]),
        "Ansi 5 Color (Light)": to_iterm2_colour(palette["light"]["magenta"]),
        "Ansi 6 Color (Dark)": to_iterm2_colour(palette["dark"]["cyan"]),
        "Ansi 6 Color (Light)": to_iterm2_colour(palette["light"]["cyan"]),
        "Ansi 7 Color (Dark)": to_iterm2_colour(palette["dark"]["background"]),
        "Ansi 7 Color (Light)": to_iterm2_colour(palette["light"]["background"]),
        "Ansi 10 Color": {
            "Alpha Component": 1.0,
            "Blue Component": 0.45524293184280396,
            "Color Space": "P3",
            "Green Component": 0.42884403467178345,
            "Red Component": 0.36227649450302124,
        },
        "Ansi 10 Color (Dark)": {
            "Blue Component": 0.4588235294117647,
            "Color Space": "sRGB",
            "Green Component": 0.43137254901960786,
            "Red Component": 0.34509803921568627,
        },
        "Ansi 10 Color (Light)": {
            "Blue Component": 0.4588235294117647,
            "Color Space": "sRGB",
            "Green Component": 0.43137254901960786,
            "Red Component": 0.34509803921568627,
        },
        "Ansi 11 Color": {
            "Alpha Component": 1.0,
            "Blue Component": 0.5097967982292175,
            "Color Space": "P3",
            "Green Component": 0.47979283332824707,
            "Red Component": 0.41305190324783325,
        },
        "Ansi 11 Color (Dark)": {
            "Blue Component": 0.5137254901960784,
            "Color Space": "sRGB",
            "Green Component": 0.4823529411764706,
            "Red Component": 0.396078431372549,
        },
        "Ansi 11 Color (Light)": {
            "Blue Component": 0.5137254901960784,
            "Color Space": "sRGB",
            "Green Component": 0.4823529411764706,
            "Red Component": 0.396078431372549,
        },
        "Ansi 12 Color": {
            "Alpha Component": 1.0,
            "Blue Component": 0.5864985585212708,
            "Color Space": "P3",
            "Green Component": 0.5783330798149109,
            "Red Component": 0.5263533592224121,
        },
        "Ansi 12 Color (Dark)": {
            "Blue Component": 0.5882352941176471,
            "Color Space": "sRGB",
            "Green Component": 0.5803921568627451,
            "Red Component": 0.5137254901960784,
        },
        "Ansi 12 Color (Light)": {
            "Blue Component": 0.5882352941176471,
            "Color Space": "sRGB",
            "Green Component": 0.5803921568627451,
            "Red Component": 0.5137254901960784,
        },
        "Ansi 13 Color": {
            "Alpha Component": 1.0,
            "Blue Component": 0.7465392351150513,
            "Color Space": "P3",
            "Green Component": 0.44249439239501953,
            "Red Component": 0.42710167169570923,
        },
        "Ansi 13 Color (Dark)": {
            "Blue Component": 0.7686274509803922,
            "Color Space": "sRGB",
            "Green Component": 0.44313725490196076,
            "Red Component": 0.4235294117647059,
        },
        "Ansi 13 Color (Light)": {
            "Blue Component": 0.7686274509803922,
            "Color Space": "sRGB",
            "Green Component": 0.44313725490196076,
            "Red Component": 0.4235294117647059,
        },
        "Ansi 14 Color": {
            "Alpha Component": 1.0,
            "Blue Component": 0.6304863095283508,
            "Color Space": "P3",
            "Green Component": 0.6296467781066895,
            "Red Component": 0.5867035984992981,
        },
        "Ansi 14 Color (Dark)": {
            "Blue Component": 0.6313725490196078,
            "Color Space": "sRGB",
            "Green Component": 0.6313725490196078,
            "Red Component": 0.5764705882352941,
        },
        "Ansi 14 Color (Light)": {
            "Blue Component": 0.6313725490196078,
            "Color Space": "sRGB",
            "Green Component": 0.6313725490196078,
            "Red Component": 0.5764705882352941,
        },
        "Ansi 15 Color": {
            "Alpha Component": 1.0,
            "Blue Component": 0.8977216482162476,
            "Color Space": "P3",
            "Green Component": 0.9656357169151306,
            "Red Component": 0.9873548150062561,
        },
        "Ansi 15 Color (Dark)": {
            "Blue Component": 0.8901960784313725,
            "Color Space": "sRGB",
            "Green Component": 0.9647058823529412,
            "Red Component": 0.9921568627450981,
        },
        "Ansi 15 Color (Light)": {
            "Blue Component": 0.8901960784313725,
            "Color Space": "sRGB",
            "Green Component": 0.9647058823529412,
            "Red Component": 0.9921568627450981,
        },
        "Ansi 8 Color": {
            "Alpha Component": 1.0,
            "Blue Component": 0.2070317268371582,
            "Color Space": "P3",
            "Green Component": 0.16550064086914062,
            "Red Component": 0.053836725652217865,
        },
        "Ansi 8 Color (Dark)": {
            "Blue Component": 0.21176470588235294,
            "Color Space": "sRGB",
            "Green Component": 0.16862745098039217,
            "Red Component": 0.0,
        },
        "Ansi 8 Color (Light)": {
            "Blue Component": 0.21176470588235294,
            "Color Space": "sRGB",
            "Green Component": 0.16862745098039217,
            "Red Component": 0.0,
        },
        "Ansi 9 Color": {
            "Alpha Component": 1.0,
            "Blue Component": 0.1624806821346283,
            "Color Space": "P3",
            "Green Component": 0.3279757499694824,
            "Red Component": 0.7377541661262512,
        },
        "Ansi 9 Color (Dark)": {
            "Blue Component": 0.08627450980392157,
            "Color Space": "sRGB",
            "Green Component": 0.29411764705882354,
            "Red Component": 0.796078431372549,
        },
        "Ansi 9 Color (Light)": {
            "Blue Component": 0.08627450980392157,
            "Color Space": "sRGB",
            "Green Component": 0.29411764705882354,
            "Red Component": 0.796078431372549,
        },
        "Badge Color": {
            "Alpha Component": 0.5,
            "Blue Component": 0.14500156044960022,
            "Color Space": "P3",
            "Green Component": 0.25274839997291565,
            "Red Component": 0.9191656708717346,
        },
        "Badge Color (Dark)": {
            "Alpha Component": 0.5,
            "Blue Component": 0.0,
            "Color Space": "sRGB",
            "Green Component": 0.1491314172744751,
            "Red Component": 1.0,
        },
        "Badge Color (Light)": {
            "Alpha Component": 0.5,
            "Blue Component": 0.0,
            "Color Space": "sRGB",
            "Green Component": 0.1491314172744751,
            "Red Component": 1.0,
        },
        "Bold Color": {
            "Alpha Component": 1.0,
            "Blue Component": 0.6304863095283508,
            "Color Space": "P3",
            "Green Component": 0.6296467781066895,
            "Red Component": 0.5867035984992981,
        },
        "Bold Color (Dark)": {
            "Blue Component": 0.6313725490196078,
            "Color Space": "sRGB",
            "Green Component": 0.6313725490196078,
            "Red Component": 0.5764705882352941,
        },
        "Bold Color (Light)": {
            "Blue Component": 0.4588235294117647,
            "Color Space": "sRGB",
            "Green Component": 0.43137254901960786,
            "Red Component": 0.34509803921568627,
        },
        "Cursor Color": {
            "Alpha Component": 1.0,
            "Blue Component": 0.5864985585212708,
            "Color Space": "P3",
            "Green Component": 0.5783330798149109,
            "Red Component": 0.5263533592224121,
        },
        "Cursor Color (Dark)": {
            "Blue Component": 0.5882352941176471,
            "Color Space": "sRGB",
            "Green Component": 0.5803921568627451,
            "Red Component": 0.5137254901960784,
        },
        "Cursor Color (Light)": {
            "Blue Component": 0.5137254901960784,
            "Color Space": "sRGB",
            "Green Component": 0.4823529411764706,
            "Red Component": 0.396078431372549,
        },
        "Cursor Guide Color": {
            "Alpha Component": 0.25,
            "Blue Component": 0.9907825589179993,
            "Color Space": "P3",
            "Green Component": 0.9204942584037781,
            "Red Component": 0.7486235499382019,
        },
        "Cursor Guide Color (Dark)": {
            "Alpha Component": 0.25,
            "Blue Component": 1.0,
            "Color Space": "sRGB",
            "Green Component": 0.9268307089805603,
            "Red Component": 0.7021318674087524,
        },
        "Cursor Guide Color (Light)": {
            "Alpha Component": 0.25,
            "Blue Component": 1.0,
            "Color Space": "sRGB",
            "Green Component": 0.9268307089805603,
            "Red Component": 0.7021318674087524,
        },
        "Cursor Text Color": {
            "Alpha Component": 1.0,
            "Blue Component": 0.2535606920719147,
            "Color Space": "P3",
            "Green Component": 0.20825165510177612,
            "Red Component": 0.08827308565378189,
        },
        "Cursor Text Color (Dark)": {
            "Blue Component": 0.25882352941176473,
            "Color Space": "sRGB",
            "Green Component": 0.21176470588235294,
            "Red Component": 0.027450980392156862,
        },
        "Cursor Text Color (Light)": {
            "Blue Component": 0.8352941176470589,
            "Color Space": "sRGB",
            "Green Component": 0.9098039215686274,
            "Red Component": 0.9333333333333333,
        },
        "Match Background Color": {
            "Alpha Component": 1.0,
            "Blue Component": 0.32116127014160156,
            "Color Space": "P3",
            "Green Component": 0.9860088229179382,
            "Red Component": 0.9969714283943176,
        },
        "Match Background Color (Dark)": {
            "Alpha Component": 1.0,
            "Blue Component": 0.32116127014160156,
            "Color Space": "P3",
            "Green Component": 0.9860088229179382,
            "Red Component": 0.9969714283943176,
        },
        "Match Background Color (Light)": {
            "Alpha Component": 1.0,
            "Blue Component": 0.32116127014160156,
            "Color Space": "P3",
            "Green Component": 0.9860088229179382,
            "Red Component": 0.9969714283943176,
        },
        "Selected Text Color": {
            "Alpha Component": 1.0,
            "Blue Component": 0.6304863095283508,
            "Color Space": "P3",
            "Green Component": 0.6296467781066895,
            "Red Component": 0.5867035984992981,
        },
        "Selected Text Color (Dark)": {
            "Blue Component": 0.6313725490196078,
            "Color Space": "sRGB",
            "Green Component": 0.6313725490196078,
            "Red Component": 0.5764705882352941,
        },
        "Selected Text Color (Light)": {
            "Blue Component": 0.4588235294117647,
            "Color Space": "sRGB",
            "Green Component": 0.43137254901960786,
            "Red Component": 0.34509803921568627,
        },
        "Selection Color": {
            "Alpha Component": 1.0,
            "Blue Component": 0.2535606920719147,
            "Color Space": "P3",
            "Green Component": 0.20825165510177612,
            "Red Component": 0.08827308565378189,
        },
        "Selection Color (Dark)": {
            "Blue Component": 0.25882352941176473,
            "Color Space": "sRGB",
            "Green Component": 0.21176470588235294,
            "Red Component": 0.027450980392156862,
        },
        "Selection Color (Light)": {
            "Blue Component": 0.8352941176470589,
            "Color Space": "sRGB",
            "Green Component": 0.9098039215686274,
            "Red Component": 0.9333333333333333,
        },
    }

    buffer = io.BytesIO()
    plistlib.dump(out, buffer, fmt=plistlib.FMT_BINARY)
    return buffer.getvalue()


if __name__ == "__main__":
    palette_id, palette = get_palette()

    out_dir = Path("out")
    out_dir.mkdir(exist_ok=True)

    (out_dir / "TextMate_light.tmTheme").write_text(
        generate_textmate_theme(colours=palette["light"], palette_id=palette_id)
    )
    (out_dir / "TextMate_dark.tmTheme").write_text(
        generate_textmate_theme(colours=palette["dark"], palette_id=palette_id)
    )
    (out_dir / "alexwlchan.itermcolors").write_bytes(generate_iterm2_theme(palette))
