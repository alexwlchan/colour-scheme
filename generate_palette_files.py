#!/usr/bin/env python3

from datetime import datetime, timezone
import json
from pathlib import Path
import textwrap

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
