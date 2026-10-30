#!/usr/bin/env python3
"""Validate serialized Flare layouts, including every native chunk combination."""
from collections import deque
from itertools import product, permutations
from pathlib import Path
import copy
import json

ROOT = Path(__file__).resolve().parents[1] / "diantre"
EXPECTED = {"florin", "udana", "yora", "abasi", "martigan", "bakat", "loren"}


def parse(path):
    sections = []
    current = None
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("["):
            current = {"section": line[1:-1], "mapmods": []}
            sections.append(current)
        elif current is not None:
            if "=" in line:
                key, value = line.split("=", 1)
                if key == "mapmod":
                    current["mapmods"].extend(value.split(";"))
                elif key == "data":
                    current["data"] = []
                else:
                    current[key] = value
            elif "data" in current:
                current["data"].append([int(v) for v in line.split(",") if v])
    return sections


def layers(sections):
    return {s["type"]: s["data"] for s in sections if s["section"] == "layer"}


def reachable(collision, start):
    q = deque([start]); seen = {start}
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p = x + dx, y + dy
            if (0 <= p[1] < len(collision) and 0 <= p[0] < len(collision[0])
                    and collision[p[1]][p[0]] == 0 and p not in seen):
                seen.add(p); q.append(p)
    return seen


def main():
    town = parse(ROOT / "maps/town/hamlet_forest.txt")
    initial = layers(town)
    kinds = ("start", "normal_a", "normal_b", "end")
    chunks = {(kind, variant): parse(ROOT / f"maps/town/compact/{kind}_{variant}.txt")
              for kind in kinds for variant in range(4)}
    normal_statuses = []
    for kind in ("normal_a", "normal_b"):
        statuses = {next(s for s in chunks[kind, v] if s["section"] == "header").get("procgen_unique_status") for v in range(4)}
        assert len(statuses) == 1 and None not in statuses, "Market family must be unique at runtime"
        normal_statuses.extend(statuses)
    assert len(set(normal_statuses)) == 2, "Market families must have different unique statuses"
    allowed_tiles = {0}
    tree_shapes = {}
    for filename in ("tilesetdefs/tileset_grassland.txt", "tilesetdefs/town/compact_palette.txt"):
        for line in (ROOT / filename).read_text().splitlines():
            if line.startswith("tile="):
                allowed_tiles.add(int(line[5:].split(",", 1)[0]))
                tid, _, _, tw, th, ox, oy = map(int, line[5:].split(","))
                if 248 <= tid <= 255:
                    tree_shapes[tid] = (tw, th, ox, oy)
    for sections in (town, *chunks.values()):
        header = next(s for s in sections if s["section"] == "header")
        width, height = int(header["width"]), int(header["height"])
        # Flare's chunk copier assumes square chunks when copying full layers.
        assert width == height, "Non-square map cannot be safely copied by Flare"
        layer_names = list(layers(sections))
        cliff_layers = [n for n in layer_names if n.startswith("cliff_")]
        assert len(cliff_layers) == 16
        assert all(layer_names.index(n) < layer_names.index("object") for n in cliff_layers), "Cliff must render behind trees"
        assert "mountain_top" not in layer_names, "No horizontal plateau over vegetation"
        for name, rows in layers(sections).items():
            assert len(rows) == height and all(len(r) == width for r in rows)
            if name != "collision":
                assert {t for row in rows for t in row} <= allowed_tiles, "Undefined tile"
    terrain_hashes = set()
    checked = 0
    for variants in product(range(4), repeat=4):
        for arrangement in permutations(kinds):
            start_index = arrangement.index("start")
            end_index = arrangement.index("end")
            # A four-cell Hamiltonian path on a 2x2 region has adjacent ends.
            if abs(start_index % 2 - end_index % 2) + abs(start_index // 2 - end_index // 2) != 1:
                continue
            checked += 1
            data = copy.deepcopy(initial); npcs = []; occupied = []
            for index, kind in enumerate(arrangement):
                sections = chunks[kind, variants[kinds.index(kind)]]
                offset_x, offset_y = (index % 2) * 12, (index // 2) * 12
                for name, rows in layers(sections).items():
                    for y, row in enumerate(rows):
                        data[name][y + offset_y][offset_x:offset_x + len(row)] = row
                for s in sections:
                    if s["section"] == "npc":
                        x, y, _, _ = map(int, s["location"].split(","))
                        npcs.append((Path(s["filename"]).stem, x + offset_x, y + offset_y))
                # Explicit footprint from actual object data, independent of builder.
                objects = layers(sections)["object"]
                for y, row in enumerate(objects):
                    for x, tile in enumerate(row):
                        if tile == 209:
                            cy = y
                            while cy > 0 and objects[cy - 1][x] in (210, 211):
                                cy -= 1
                            assert cy + offset_y >= 5, "Cabin roof too close to the cliff"
                            occupied.extend((cx + offset_x, yy + offset_y)
                                            for yy in range(cy, y + 1) for cx in (x - 1, x))
                if kind == "start":
                    spawn = (offset_x + 6, offset_y + 10)
            for s in town:
                for component in s["mapmods"]:
                    layer, x, y, tile = component.split(",")
                    data[layer][int(y)][int(x)] = int(tile)
            c = data["collision"]
            trees = [(x, y, tree_shapes[t]) for y, row in enumerate(data["object"])
                     for x, t in enumerate(row) if t in tree_shapes]
            seen = reachable(c, spawn)
            assert len(npcs) == 7 and {n for n, _, _ in npcs} == EXPECTED, npcs
            assert len({(x, y) for _, x, y in npcs}) == 7
            assert c[spawn[1]][spawn[0]] == 0, spawn
            for name, x, y in npcs:
                assert (x, y) in seen, (variants, arrangement, "unreachable merchant", name)
                assert any((x + dx, y + dy) in seen for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                for tx, ty, (tw, th, ox, oy) in trees:
                    if tx+ty < x+y:
                        continue
                    left = ((tx-x)-(ty-y))*96-ox
                    top = ((tx-x)+(ty-y))*48-oy
                    for body_y in (-120, -60):
                        assert not (left <= 0 < left+tw and top <= body_y < top+th), ("Tree can hide merchant", name, (x,y), (tx,ty))
            assert (12, 3) in seen and (12, 4) in seen, "Dungeon entrance disconnected"
            assert any(p in seen for p in ((13, 14), (15, 14), (14, 13), (14, 15))), "Stash disconnected"
            assert all(c[y][x] == 1 for x, y in occupied), "Walkable cabin footprint"
            assert all(c[y][x] == 1 for y in range(3) for x in range(len(c[0]))), "Passage behind mountain"
            assert all(c[0][x] == c[-1][x] == 1 for x in range(len(c[0])))
            assert all(row[0] == row[-1] == 1 for row in c)
            terrain_hashes.add(tuple(tuple(r) for r in data["object"]))
    print(json.dumps({"combinations_checked": checked, "distinct_layouts": len(terrain_hashes),
                      "merchants_per_layout": 7, "entrance": [12, 3],
                      "checks": ["merchant access", "cabin footprints", "north entrance access",
                                 "stash access", "mountain inaccessible", "closed perimeter",
                                 "merchant canopy clearance", "roof setback", "cliff layer order"]}, indent=2))


if __name__ == "__main__":
    main()
