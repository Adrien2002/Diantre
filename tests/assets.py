#!/usr/bin/env python3
"""Audit the bundled files independently of the original campaign installation."""
import hashlib
import json
import os
from pathlib import Path
import sys

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "tools"))
from import_assets import active_lines, references


def main():
    mod = PROJECT / "mods/diantre"
    flare_home = Path(os.environ.get("FLARE_HOME", str(Path.home() / "Games/Flare")))
    default = Path(os.environ.get("FLARE_DEFAULT", str(flare_home / "mods/default")))
    manifest = json.loads((mod / "ASSET_MANIFEST.json").read_text())
    errors = []
    for name, record in manifest["files"].items():
        path = mod / name
        if not path.is_file() or path.is_symlink():
            errors.append(f"Missing file or symlink: {name}")
            continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
            errors.append(f"Changed since extraction: {name}")
        if path.suffix == ".txt":
            for ref in references(path.read_text()):
                if not (mod / ref).is_file() and not (default / ref).is_file():
                    errors.append(f"Missing dependency: {name} -> {ref}")
    assert not errors, "\n".join(errors)
    settings = (mod / "settings.txt").read_text()
    assert "requires=" not in settings
    assert "game=diantre" in settings
    assert list(active_lines((mod / "engine/languages.txt").read_text())) == ["en=English"]
    assert not list((mod / "languages").glob("*.po")), "Prototype must not bundle non-English catalogs"
    maps = list((mod / "maps").rglob("*.txt"))
    for path in maps:
        name = path.relative_to(mod).as_posix()
        assert name == "maps/spawn.txt" or name.startswith(
            ("maps/town/", "maps/iron_labyrinth", "maps/procgen_rules/iron_labyrinth")), name
        for line in active_lines(path.read_text()):
            if line.startswith("intermap="):
                assert line.startswith(("intermap=maps/iron_labyrinth", "intermap=maps/town/")), (name, line)
    assert not (mod / "maps/iron_labyrinth/warp_room.txt").exists()
    assert not (mod / "maps/iron_labyrinth_chasm.txt").exists(), "No fixed boss map"
    for name in ("tilesetdefs/tileset_grassland.txt", "music/town_theme.ogg",
                 "licenses/flare-game/CREDITS.txt", "licenses/flare-game/NOTICE.md",
                 "licenses/flare-game/LICENSE-CC-BY-SA-3.0.txt",
                 "licenses/flare-game/LICENSE-FONTS-OFL.txt"):
        assert (mod / name).is_file(), name
    assert list((mod / "images/npcs").glob("*.png"))
    print(f"PASS: {len(manifest['files'])} bundled files verified; dependencies resolved; "
          f"{len(maps)} town/dungeon map/chunk/rule files, no external campaign maps; licenses present.")


if __name__ == "__main__":
    main()
