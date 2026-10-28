#!/usr/bin/env python3
"""Check every authored surface variant against every possible connector mask."""
from pathlib import Path
import sys
from map_data import connected, sections

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "tools"))
from build_town import BIOMES, CHUNK_SIZE, PADDING, REGION, WORLD


def main():
    mod = PROJECT / "mods/diantre"
    ids = set()
    bounds = {}
    for path in [mod / "tilesetdefs/tileset_grassland.txt", *(mod / "tilesetdefs/town").glob("*.txt")]:
        for line in path.read_text().splitlines():
            if line.startswith("tile="):
                tile, sx, sy, width, height, ox, oy = map(int, line[5:].split(","))
                assert tile not in ids, (path, tile, "duplicate palette tile ID")
                ids.add(tile)
                bounds[tile] = height, oy
    cases = 0
    for biome in BIOMES:
        directory = mod / "maps/town/chunks" / biome
        parent_layers = [s["type"] for s in sections((mod / f"maps/town/{biome}.txt").read_text())
                         if s["section"] == "layer"]
        links = sections((directory / "links_0.txt").read_text())
        strips = [tuple(map(int, s["location"].split(","))) for s in links if "procgen_link" in s]
        for path in directory.glob("*.txt"):
            data = sections(path.read_text())
            assert [s["type"] for s in data if s["section"] == "layer"] == parent_layers, (path, "inconsistent native layer order")
            assert not [s for s in data if s["section"] == "enemy"], path
            for s in data:
                if s["section"] == "layer" and s.get("type") != "collision":
                    assert all(tile in ids for row in s["data"] for tile in row if tile), path
            if path.name.startswith("links"):
                continue
            base = next(s["data"] for s in data if s.get("type") == "collision")
            start = tuple(map(int, data[0]["hero_pos"].split(",")))
            scenery = {s["type"]: s["data"] for s in data
                       if s.get("type") == "object" or s.get("type", "").startswith("cliff_")}
            for mask in range(1, 16):
                collision = [row[:] for row in base]
                rendered = {name: [row[:] for row in values] for name, values in scenery.items()}
                visible = rendered["object"]
                for i, (x, y, w, h) in enumerate(strips):
                    if mask & (1 << i):
                        for yy in range(y, y+h):
                            for xx in range(x, x+w):
                                collision[yy][xx] = 0
                                for values in rendered.values():
                                    values[yy][xx] = 0
                reach = connected(collision, start)
                # Cover a 3440x1440 viewport at every legal edge placement.
                # Native generation has no links leading outside its grid.
                extent = 3440/384 + 1440/192
                cells = REGION // CHUNK_SIZE
                for cy in range(cells):
                    for cx in range(cells):
                        if ((cy == 0 and mask & 1) or (cy == cells-1 and mask & 2) or
                                (cx == 0 and mask & 4) or (cx == cells-1 and mask & 8)):
                            continue
                        xs = [xx + cx*CHUNK_SIZE + 0.5 for xx, yy in reach]
                        ys = [yy + cy*CHUNK_SIZE + 0.5 for xx, yy in reach]
                        assert min(xs) >= extent and min(ys) >= extent, (path, mask, "exposed near map edge")
                        assert max(xs)+extent < WORLD and max(ys)+extent < WORLD, (path, mask, "exposed far map edge")
                for i, (x, y, w, h) in enumerate(strips):
                    if mask & (1 << i):
                        assert (x+w//2, y+h//2) in reach, (path, mask, "blocked connector")
                for s in data:
                    if s.get("script") == "scripts/town/enter_dungeon.txt" or s["section"] == "npc":
                        pos = tuple(map(int, s["location"].split(",")[:2]))
                        assert pos in reach, (path, mask, "unreachable entrance/vendor")
                    if s.get("script") == "scripts/town/enter_dungeon.txt":
                        x, y = map(int, s["location"].split(",")[:2])
                        offset = 1000 if biome == "snow" else 0
                        assert visible[y-1][x:x+2] == [offset + 226, offset + 227], (path, mask, "hidden cave mouth")
                        # A continuous, blocked landmass must back the opening.
                        # Check every terrain layer after native link overlays.
                        tops = scenery["cliff_tops"]
                        plateau = {(xx, yy) for yy, row in enumerate(tops)
                                   for xx, tile in enumerate(row) if tile}
                        assert len(plateau) >= 20, (path, mask, "missing cliff plateau")
                        upper_tops = [name for name in scenery if name.startswith("cliff_tops_")]
                        assert len(upper_tops) == 2, (path, mask, "missing hillside terraces")
                        previous = plateau
                        for name in upper_tops:
                            footprint = {(xx, yy) for yy, row in enumerate(scenery[name])
                                         for xx, tile in enumerate(row) if tile}
                            assert footprint and footprint < previous, (path, mask, "unsupported upper terrace")
                            assert max(xx for xx, yy in footprint) < max(xx for xx, yy in previous), (path, mask, "terrace has no side setback")
                            assert max(yy for xx, yy in footprint) < max(yy for xx, yy in previous), (path, mask, "terrace has no front setback")
                            previous = footprint
                        for xx, yy in plateau:
                            assert collision[yy][xx] == 1, (path, mask, "walkable plateau")
                            for name in scenery.keys() - {"object"}:
                                assert rendered[name][yy][xx] == scenery[name][yy][xx], (path, mask, "cliff cut by connector")
                            if yy != y-1 or xx not in (x, x+1):
                                assert not visible[yy][xx], (path, mask, "freestanding cliff props")
                        left, right = min(xx for xx, yy in plateau), max(xx for xx, yy in plateau)
                        wall = rendered["cliff_faces"][y-1]
                        assert all(wall[xx] for xx in range(left, right+1)
                                   if xx not in (x, x+1)), (path, mask, "gap in cave wall")
                        assert all(rendered["cliff_faces_upper"][y-1][xx]
                                   for xx in range(left, right+1)), (path, mask, "gap in upper entrance wall")
                        # Compare the arch with the nearest corners of the
                        # adjacent terrain diamonds, including the isometric
                        # shift between tiles. Both flanks must cover its top.
                        arch_top = min((xx+y-1)*48 - bounds[visible[y-1][xx]][1]
                                       for xx in (x, x+1))
                        lip_bottom = max((xx+y-1)*48 + bounds[tops[y-1][xx]][0]//2 - bounds[tops[y-1][xx]][1]
                                         for xx in (x-1, x+2))
                        assert lip_bottom < arch_top, (path, mask, "cave arch protrudes above cliff")
                        assert all((xx, y-2) in plateau for xx in (x, x+1)), (path, mask, "unsupported cave opening")
                        assert (x+1, y) in reach, (path, mask, "blocked entrance apron")
                        assert not any(visible[yy][xx] in BIOMES[biome].decorations
                                       for yy in range(y, PADDING+14) for xx in range(PADDING+1, PADDING+12)), (path, mask, "overgrown entrance clearing")
                    if s.get("intermap_id") == "dungeon_exit":
                        pos = tuple(map(int, s["location"].split(",")[:2]))
                        assert pos in reach, (path, mask, "blocked dungeon return")
                    if s.get("stash") == "true":
                        x, y = map(int, s["location"].split(",")[:2])
                        assert visible[y][x] == 297, (path, mask, "hidden stash")
                if path.name.startswith("start"):
                    assert visible[PADDING+5][PADDING+2] != 0, (path, mask, "hidden house")
                cases += 1
    print(f"PASS: {len(BIOMES)} biomes, {cases} variant/link configurations; "
          "all tiles defined, no surface enemies, accessible links/entrances/vendors.")


if __name__ == "__main__":
    main()
