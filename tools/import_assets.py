#!/usr/bin/env python3
"""Build a standalone Diantre mod from local, unmodified Flare game sources.

Output must be empty. Source paths, transformations and hashes are recorded;
existing project files are never replaced by this command.
"""
import argparse
from collections import defaultdict, deque
import hashlib
import json
from pathlib import Path
import re
from update_translations import write_catalog

PROJECT = Path(__file__).resolve().parents[1]
GAME_REVISION = "af6eee6d339ac98011864bfe89da837fe7769c28"
PATH_REF = re.compile(r"(?<![\w./])((?:animations|books|cutscenes|enemies|engine|fonts|images|items|languages|loot|maps|menus|music|npcs|powers|scripts|soundfx|tilesetdefs)/[^,;\s=]+)")
FONT_REF = re.compile(r"(?<![/\w.-])([\w.-]+\.(?:ttf|otf))\b")


def meaningful(text):
    return [line.strip() for line in text.splitlines()
            if line.strip() and not line.lstrip().startswith("#")]


def active_lines(text):
    """Tiled's editor-only tilesheet paths are not runtime dependencies."""
    section = ""
    for line in meaningful(text):
        if line.startswith("["):
            section = line
        if section != "[tilesets]":
            yield line


def references(text):
    for line in active_lines(text):
        yield from PATH_REF.findall(line)
        for font in FONT_REF.findall(line):
            yield "fonts/" + font


def translation_catalogs(names, language_table):
    enabled = {line.split("=", 1)[0] for line in meaningful(language_table) if "=" in line}
    return [name for name in names if name.startswith("languages/") and name.endswith(".po")
            and name.rsplit(".", 2)[-2] in enabled]


def adapt(name, text):
    changes = []
    if name == "powers/powers.txt":
        text = text.replace("script=on_cast,scripts/powers/dev_tome.txt\n", "")
        changes.append("disabled Empyrean campaign developer tome")
    if name.startswith("maps/iron_labyrinth") or name == "scripts/powers/perdition_scroll.txt":
        blocks = []
        for block in re.split(r"(?m)(?=^\[)", text):
            lines = []
            for line in block.splitlines():
                if line.startswith("intermap=maps/"):
                    target = line.split("=", 1)[1].split(",", 1)[0]
                    if not target.startswith("maps/iron_labyrinth") or target == "maps/iron_labyrinth_chasm.txt":
                        line = "script=scripts/town/return.txt"
                        changes.append("external exit now returns to the saved procedural town")
                if line == "tooltip=Perdition Harbor Cave":
                    line = "tooltip=Return to Town"
                if line == "tooltip=Iron Labyrinth: Chasm":
                    line = "tooltip=Return to Town"
                lines.append(line)
            blocks.append("\n".join(lines))
        text = "\n".join(blocks) + "\n"
    if name.startswith("maps/procgen_rules/iron_labyrinth_f"):
        text = text.replace("filename=maps/iron_labyrinth/warp_room.txt\n", "")
        changes.append("removed room that teleports into Empyrean quest maps")
    return text, sorted(set(changes))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="flare-game source root")
    parser.add_argument("--default", type=Path, required=True, help="engine's mods/default")
    parser.add_argument("--output", type=Path, required=True, help="new/empty mod directory")
    args = parser.parse_args()
    if args.output.exists() and any(args.output.iterdir()):
        parser.error("Output must be empty; rebuild elsewhere to preserve edits.")
    sources = [("fantasycore", args.source / "mods/fantasycore"),
               ("empyrean_campaign", args.source / "mods/empyrean_campaign"),
               ("diantre", PROJECT / "campaign/diantre")]
    index = defaultdict(list)
    for label, root in sources:
        if not root.is_dir():
            parser.error(f"Missing source mod: {root}")
        for path in sorted(root.rglob("*")):
            if path.is_file():
                index[path.relative_to(root).as_posix()].append((label, path))

    def content(name):
        layers = index[name]
        if Path(name).suffix != ".txt":
            return layers[-1][1].read_bytes(), [layers[-1]], []
        chain = []
        append = False
        for label, path in layers:
            text = path.read_text()
            lines = meaningful(text)
            if not lines or lines[0] != "APPEND":
                chain = []
                append = False
            elif not chain:
                append = True  # still append to the engine's default mod
            text = "\n".join(x for x in text.splitlines() if x.strip() != "APPEND")
            chain.append((label, path, text))
        text = ("APPEND\n" if append else "") + "\n\n".join(x[2] for x in chain) + "\n"
        text, changes = adapt(name, text)
        return text.encode(), [(x[0], x[1]) for x in chain], changes

    # Keep all class/equipment combinations and the full powers/item catalogue;
    # their animation filenames and summoned enemy categories are dynamic.
    prefixes = ("engine/", "menus/", "powers/", "items/", "loot/",
                "animations/avatar/", "animations/loot/", "animations/npcs/",
                "images/menus/", "images/npcs/", "soundfx/", "fonts/", "tilesetdefs/")
    queue = deque(name for name in index if name.startswith(prefixes))
    # Follow the native language table. Only English is enabled now; adding a
    # supported language/catalog later requires data changes, not code changes.
    queue.extend(translation_catalogs(index, content("engine/languages.txt")[0].decode()))
    queue.extend(["settings.txt", "maps/spawn.txt", "maps/iron_labyrinth_f1.txt",
                  "maps/iron_labyrinth_f2.txt", "maps/iron_labyrinth_f3.txt",
                  "tilesetdefs/tileset_grassland.txt",
                  "music/town_theme.ogg", "cutscenes/intro.txt", "cutscenes/credits.txt",
                  "animations/hero.txt"])

    categories = defaultdict(set)
    for name in index:
        if name.startswith("enemies/") and name.count("/") == 1:
            for line in meaningful(content(name)[0].decode()):
                if line.startswith("categories="):
                    for category in line.split("=", 1)[1].split(","):
                        categories[category].add(name)
    records = {}
    missing = set()
    while queue:
        name = queue.popleft()
        if name in records:
            continue
        if name not in index:
            if not (args.default / name).is_file():
                missing.add(name)
            continue
        if name.startswith("maps/") and not (name == "maps/spawn.txt" or
                name.startswith(("maps/town/", "maps/iron_labyrinth", "maps/procgen_rules/iron_labyrinth"))):
            raise RuntimeError(f"Unexpected campaign map dependency: {name}")
        data, origins, changes = content(name)
        target = args.output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        records[name] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
                         "sources": [label + "/" + name for label, _ in origins],
                         "changes": changes}
        if target.suffix == ".txt":
            text = data.decode()
            queue.extend(references(text))
            for line in active_lines(text):
                if line.startswith(("category=", "spawn_type=")):
                    queue.extend(sorted(categories[line.split("=", 1)[1].split(",")[0]]))
                elif line.startswith("spawn="):
                    for spawn in line.split("=", 1)[1].split(";"):
                        queue.extend(sorted(categories[spawn.split(",")[0]]))

    # Retain game overrides of files whose names are implicit in engine defaults.
    # The UI atlas families, NPCs and sounds above also cover dynamic lookups.
    for path in args.default.rglob("*.txt"):
        for name in references(path.read_text()):
            if name in index and name not in records:
                raise RuntimeError(f"Engine-default dependency not selected: {name}")

    template = write_catalog(args.output)
    data = template.read_bytes()
    records["languages/data.pot"] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
                                     "sources": ["diantre/localization template"],
                                     "changes": ["extracted English msgids with Flare data keys"]}
    manifest = {"source": "https://github.com/flareteam/flare-game",
                "revision": GAME_REVISION, "scope": "procedural_town_and_iron_labyrinth",
                "missing_in_upstream": sorted(missing), "files": dict(sorted(records.items()))}
    (args.output / "ASSET_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    for path in (PROJECT / "third_party/flare-game").iterdir():
        if path.is_file():
            target = args.output / "licenses/flare-game" / path.name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(path.read_bytes())
    print(f"Imported {len(records)} files, {sum(x['bytes'] for x in records.values()) / 2**20:.1f} MiB")
    print("Missing in upstream:", sorted(missing))


if __name__ == "__main__":
    main()
