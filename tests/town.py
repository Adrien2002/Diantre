#!/usr/bin/env python3
"""Check every authored surface variant against every possible connector mask."""
from pathlib import Path
import sys
from map_data import connected, sections

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "tools"))
from build_town import BIOMES


def main():
    mod = PROJECT / "mods/diantre"
    ids = set()
    for path in [mod / "tilesetdefs/tileset_grassland.txt", *(mod / "tilesetdefs/town").glob("*.txt")]:
        for line in path.read_text().splitlines():
            if line.startswith("tile="):
                ids.add(int(line[5:].split(",")[0]))
    cases = 0
    for biome in BIOMES:
        directory = mod / "maps/town/chunks" / biome
        links = sections((directory / "links_0.txt").read_text())
        strips = [tuple(map(int, s["location"].split(","))) for s in links if "procgen_link" in s]
        for path in directory.glob("*.txt"):
            data = sections(path.read_text())
            assert not [s for s in data if s["section"] == "enemy"], path
            for s in data:
                if s["section"] == "layer" and s.get("type") != "collision":
                    assert all(tile in ids for row in s["data"] for tile in row if tile), path
            if path.name.startswith("links"):
                continue
            base = next(s["data"] for s in data if s.get("type") == "collision")
            objects = next(s["data"] for s in data if s.get("type") == "object")
            for mask in range(1, 16):
                collision = [row[:] for row in base]
                visible = [row[:] for row in objects]
                for i, (x, y, w, h) in enumerate(strips):
                    if mask & (1 << i):
                        for yy in range(y, y+h):
                            for xx in range(x, x+w):
                                collision[yy][xx] = 0
                                visible[yy][xx] = 0
                reach = connected(collision, (8, 10))
                for i, (x, y, w, h) in enumerate(strips):
                    if mask & (1 << i):
                        assert (x+w//2, y+h//2) in reach, (path, mask, "blocked connector")
                for s in data:
                    if s.get("script") == "scripts/town/enter_dungeon.txt" or s["section"] == "npc":
                        pos = tuple(map(int, s["location"].split(",")[:2]))
                        assert pos in reach, (path, mask, "unreachable entrance/vendor")
                    if s.get("script") == "scripts/town/enter_dungeon.txt":
                        x, y = map(int, s["location"].split(",")[:2])
                        assert visible[y-1][x:x+2] == [226, 227], (path, mask, "hidden cave mouth")
                    if s.get("stash") == "true":
                        x, y = map(int, s["location"].split(",")[:2])
                        assert visible[y][x] == 297, (path, mask, "hidden stash")
                if path.name.startswith("start"):
                    assert visible[5][2] != 0, (path, mask, "hidden house")
                cases += 1
    print(f"PASS: {len(BIOMES)} biomes, {cases} variant/link configurations; "
          "all tiles defined, no surface enemies, accessible links/entrances/vendors.")


if __name__ == "__main__":
    main()
