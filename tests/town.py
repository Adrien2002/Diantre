#!/usr/bin/env python3
"""Check all open-town lot arrangements and preserve the terraced cave entrance."""
from itertools import permutations, product
from pathlib import Path
import sys
from map_data import check_open_square, sections, surface_layers

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "tools"))
from build_town import BIOMES, CHUNK_SIZE, VARIANTS


def check_hillside(data, biome, bounds):
    layers = {s["type"]: s["data"] for s in data if s["section"] == "layer"}
    door = next(s for s in data if s.get("script") == "scripts/town/enter_dungeon.txt")
    x, y = map(int, door["location"].split(",")[:2])
    offset = 1000 if biome == "snow" else 0
    visible, collision = layers["object"], layers["collision"]
    assert visible[y-1][x:x+2] == [offset+226, offset+227], "Hidden cave mouth"
    tops = layers["cliff_tops"]
    plateau = {(xx, yy) for yy, row in enumerate(tops) for xx, tile in enumerate(row) if tile}
    assert len(plateau) >= 20, "Missing cliff plateau"
    previous = plateau
    for name in ("cliff_tops_2", "cliff_tops_3"):
        footprint = {(xx, yy) for yy, row in enumerate(layers[name]) for xx, tile in enumerate(row) if tile}
        assert footprint and footprint < previous, "Unsupported upper terrace"
        assert max(xx for xx, yy in footprint) < max(xx for xx, yy in previous), "No side setback"
        assert max(yy for xx, yy in footprint) < max(yy for xx, yy in previous), "No front setback"
        previous = footprint
    for xx, yy in plateau:
        assert collision[yy][xx] == 1, "Walkable plateau"
        if yy != y-1 or xx not in (x, x+1):
            assert visible[yy][xx] == 0, "Freestanding cliff props"
    left, right = min(xx for xx, yy in plateau), max(xx for xx, yy in plateau)
    assert all(layers["cliff_faces"][y-1][xx] for xx in range(left, right+1)
               if xx not in (x, x+1)), "Gap in cave wall"
    assert all(layers["cliff_faces_upper"][y-1][xx] for xx in range(left, right+1)), "Gap in upper wall"
    arch_top = min((xx+y-1)*48 - bounds[visible[y-1][xx]][1] for xx in (x, x+1))
    lip_bottom = max((xx+y-1)*48 + bounds[tops[y-1][xx]][0]//2 - bounds[tops[y-1][xx]][1]
                     for xx in (x-1, x+2))
    assert lip_bottom < arch_top, "Cave arch protrudes above cliff"
    assert all((xx, y-2) in plateau for xx in (x, x+1)), "Unsupported cave opening"
    assert collision[y][x] == collision[y][x+1] == 0, "Blocked entrance apron"
    assert not any(visible[yy][xx] in BIOMES[biome].decorations
                   for yy in range(y, 31) for xx in range(16, 31)), "Overgrown entrance"


def main():
    mod = PROJECT / "mods/diantre"
    bounds = {}
    for path in [mod / "tilesetdefs/tileset_grassland.txt", *(mod / "tilesetdefs/town").glob("*.txt")]:
        for line in path.read_text().splitlines():
            if line.startswith("tile="):
                tile, sx, sy, width, height, ox, oy = map(int, line[5:].split(","))
                assert tile not in bounds, (path, tile, "Duplicate palette ID")
                bounds[tile] = height, oy
    # All legal native paths through four lots in a 2x2 region, in either direction.
    corners = ((0, 0), (1, 0), (0, 1), (1, 1))
    layouts = [p for p in permutations(corners, 4)
               if all(abs(a[0]-b[0])+abs(a[1]-b[1]) == 1 for a, b in zip(p, p[1:]))]
    assert len(layouts) == 8
    expected = {f"npcs/town/{name}.txt" for name in
                ("udana", "florin", "yora", "abasi", "bakat", "martigan", "loren")}
    for name in expected:
        profile = (mod / name).read_text()
        assert "vendor=true" in profile and "talker=false" in profile, name
        assert not any(line.startswith(("vendor_requires", "status_stock=", "[dialog]", "INCLUDE "))
                       for line in profile.splitlines()), (name, "Shop depends on campaign quests")
        assert "constant_stock=" in profile or "random_stock=" in profile, (name, "Empty shop")
    cases = 0
    for biome in BIOMES:
        parent = sections((mod / f"maps/town/{biome}.txt").read_text())
        layer_order = [s["type"] for s in parent if s["section"] == "layer"]
        chunks = {}
        for path in (mod / "maps/town/chunks" / biome).glob("*.txt"):
            data = sections(path.read_text())
            assert [s["type"] for s in data if s["section"] == "layer"] == layer_order, path
            assert not any(s["section"] == "enemy" for s in data), path
            for s in data:
                if s["section"] == "layer" and s["type"] != "collision":
                    assert all(tile in bounds for row in s["data"] for tile in row if tile), path
            if path.name.startswith("end"):
                check_hillside(data, biome, bounds)
            chunks[path.stem] = data
        links = chunks["links_0"]
        for entry in links:
            if "procgen_link" in entry:
                x, y, w, h = map(int, entry["location"].split(","))
                for name, values in surface_layers(links).items():
                    if name not in ("background_base", "background"):
                        assert all(values[yy][xx] == 0 for yy in range(y, y+h) for xx in range(x, x+w)), "Link overwrites a town feature"
        for layout, market_order, variants in product(layouts, permutations((0, 1)),
                                                       product(range(VARIANTS), repeat=4)):
            layers = {s["type"]: [row[:] for row in s["data"]]
                      for s in parent if s["section"] == "layer" and s["type"] in ("collision", "object")}
            targets, homes, merchants = [], [], []
            choices = (variants[0], market_order[0]*VARIANTS+variants[1],
                       market_order[1]*VARIANTS+variants[2], variants[3])
            for role, (cx, cy), variant in zip(("start", "normal", "normal", "end"), layout, choices):
                data = chunks[f"{role}_{variant}"]
                ox, oy = cx*CHUNK_SIZE, cy*CHUNK_SIZE
                for entry in data:
                    if entry["section"] == "layer" and entry["type"] in layers:
                        for y, row in enumerate(entry["data"], oy):
                            layers[entry["type"]][y][ox:ox+CHUNK_SIZE] = row
                    if entry.get("script") == "scripts/town/enter_dungeon.txt" or entry["section"] == "npc" or entry.get("intermap_id") or entry.get("stash"):
                        x, y = map(int, entry["location"].split(",")[:2])
                        targets.append((x+ox, y+oy))
                    if role == "start" and entry["section"] == "header":
                        x, y = map(int, entry["hero_pos"].split(","))
                        start = x+ox, y+oy
                    if entry["section"] == "npc":
                        x, y = map(int, entry["location"].split(",")[:2])
                        homes.append((x+ox-3, y+oy-2))
                        merchants.append(entry["filename"])
            # Native on-load perimeter/plaza events act on the assembled town.
            assembled = [{"section": "layer", "type": name, "data": values}
                         for name, values in layers.items()]
            assembled.extend(s for s in parent if s["section"] == "event" and "mapmod" in s)
            layers = surface_layers(assembled)
            try:
                reachable = check_open_square(layers, start)
            except AssertionError as error:
                raise AssertionError((biome, layout, market_order, variants, str(error))) from error
            assert all(pos in reachable for pos in targets), (biome, layout, variants, "Unreachable service or entrance")
            assert len(merchants) == 7 and set(merchants) == expected, "Missing or repeated merchant"
            assert len(homes) == len(set(homes)) == 7
            assert all(layers["object"][y][x] == BIOMES[biome].house for x, y in homes), "Missing merchant house"
            cases += 1
    print(f"PASS: {len(BIOMES)} biomes, {cases} complete town arrangements; open plaza and broad approaches, "
          "seven unique merchant houses, accessible entrance, intact hillsides and safe borders.")


if __name__ == "__main__":
    main()
