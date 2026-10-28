#!/usr/bin/env python3
"""Extract English Flare data messages into the native languages/data.pot template."""
import argparse
from collections import defaultdict
import json
from pathlib import Path

# Message keys supported by Flare's data extractor and MessageEngine.
PLAIN = {
    "msg", "him", "her", "you", "name", "title", "tooltip", "quest_text",
    "description", "topic", "flavor", "caption", "text",
}
KEYS = PLAIN | {
    "power_desc", "tab_title", "currency_name", "option", "name_short",
    "text_base", "text_base_desc", "text_regen", "text_regen_desc", "text_steal",
    "text_steal_desc", "text_resist_steal", "text_resist_steal_desc",
    "text_combat_heal", "text_log_restore", "text_log_low", "text_tooltip_heal",
    "text_tooltip_cost", "tooltip_text_shield", "tooltip_text_heal",
}


def catalog(mod):
    messages = defaultdict(list)
    for path in sorted(mod.rglob("*.txt")):
        if "licenses" in path.relative_to(mod).parts:
            continue
        for number, line in enumerate(path.read_text().splitlines(), 1):
            if "=" not in line or line.lstrip().startswith("#"):
                continue
            key, value = line.split("=", 1)
            if key not in KEYS or not value.strip():
                continue
            if key not in PLAIN:
                fields = value.split(",")
                if key == "option":
                    value = fields[-1]
                elif len(fields) == 2:
                    value = fields[0]
                elif len(fields) == 3:
                    value = fields[1]
            value = value.strip()
            if value:
                messages[value].append(f"{path.relative_to(mod).as_posix()}:{number}")
    lines = [
        "# Diantre game data translation template.",
        "# Game data and this template are licensed under CC-BY-SA-3.0.",
        "# Keep English msgids unchanged; translate msgstr in data.<language>.po.",
        'msgid ""', 'msgstr ""',
        '"Project-Id-Version: Diantre\\n"', '"Language: \\n"',
        '"MIME-Version: 1.0\\n"', '"Content-Type: text/plain; charset=UTF-8\\n"',
        '"Content-Transfer-Encoding: 8bit\\n"', "",
    ]
    for message, locations in sorted(messages.items()):
        lines.extend(["#: " + " ".join(locations),
                      "msgid " + json.dumps(message, ensure_ascii=False), 'msgstr ""', ""])
    return "\n".join(lines) + "\n"


def write_catalog(mod, output=None):
    output = output or mod / "languages/data.pot"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(catalog(mod))
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mod", type=Path, default=Path(__file__).resolve().parents[1] / "mods/diantre")
    args = parser.parse_args()
    print(write_catalog(args.mod))
