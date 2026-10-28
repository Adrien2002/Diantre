#!/usr/bin/env python3
"""Author reusable surface chunks; Flare randomizes their layout in each save.

No Python runs while playing. Seeded Random below only makes the collection of
chunk variants reproducible. Flare's native procgen selects and connects them.
"""
from pathlib import Path
import argparse
from dataclasses import dataclass
import random

ROOT = Path(__file__).resolve().parents[1] / "campaign/diantre"
SIZE = 16
REGION = 64
WORLD = 80  # decorative margin beyond the generated, explorable region
@dataclass(frozen=True)
class Biome:
    title: str
    decorations: tuple
    ground_tiles: tuple
    density: float = 0.12
    house: int = 296


BIOMES = {
    "forest": Biome("Conifer Clearing", (248, 249, 250, 251), tuple(range(16, 32)), 0.19),
    "woodland": Biome("Woodland Hamlet", (252, 253, 254, 255), tuple(range(16, 32)), 0.17),
    "rocky": Biome("Rocky Hamlet", (132, 133, 134, 135, 136, 137), tuple(range(32, 48))),
    "swamp": Biome("Marsh Refuge", (245, 246, 247, 252), tuple(range(16, 32))),
    "meadow": Biome("Meadow Village", (112, 113, 114, 115, 116, 117), tuple(range(16, 32)), 0.08),
    "coast": Biome("Riverside Outpost", (132, 134, 245, 247), tuple(range(16, 32)), 0.09),
    "snow": Biome("Snow Refuge", (1244, 1245, 1246, 1247, 1132, 1134), tuple(range(1016, 1032)), house=1744),
    "cave": Biome("Underground Hamlet", (2128, 2129, 2130, 2131, 2132, 2134), tuple(range(2021, 2029))),
    "ruins": Biome("Ruins Camp", (3282, 3283, 3284, 3285, 3286, 3287), tuple(range(3024, 3032))),
    "citadel": Biome("Forgotten Citadel", (4123, 4124, 4125, 4126, 4127), tuple(range(4032, 4048))),
}


def write(name, text):
    target = ROOT / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)


def grid(n, value):
    return [[value for _ in range(n)] for _ in range(n)]


def layer(name, values):
    return "\n[layer]\ntype=" + name + "\ndata=\n" + "\n".join(
        ",".join(str(x) for x in row) for row in values) + "\n"


def event(x, y, *components, width=1, height=1):
    return (f"\n[event]\ntype=event\nlocation={x},{y},{width},{height}\n" +
            "\n".join(components) + "\n")


def block(collision, x, y, w=1, h=1):
    for yy in range(max(0, y), min(len(collision), y+h)):
        for xx in range(max(0, x), min(len(collision), x+w)):
            collision[yy][xx] = 1


def ground(biome, x, y):
    tiles = BIOMES[biome].ground_tiles
    return tiles[(x % 4 + (y % 4) * 4) % len(tiles)]


def dungeon_entrance(biome, variant, bg, obj, col):
    # Reserve a complete rocky outcrop outside the native connector strips.
    # The mouth and its supporting rock must survive every link combination.
    # Keep the landmark away from the foreground edge: trees in neighbouring
    # chunks can overhang several tiles. The end chunk itself is still random.
    x, y = [(3, 5), (2, 5), (3, 4)][variant]
    left, right = 1, 5
    back, front = y - 3, y - 1
    offset = 1000 if biome == "snow" else 0
    # A clearing lets the player see the mouth beneath the tall forest canopy.
    for yy in range(1, 14):
        for xx in range(1, 12):
            if obj[yy][xx]:
                obj[yy][xx] = 0
                if 2 <= xx < SIZE - 2 and 2 <= yy < SIZE - 2:
                    col[yy][xx] = 0
    for yy in range(back, min(SIZE - 1, y + 2)):
        for xx in range(left, right + 1):
            obj[yy][xx], col[yy][xx] = 0, 0
            bg[yy][xx] = ground(biome, xx, yy)
    # Solid, textured columns give the cliff depth and a closed silhouette.
    # These are the existing natural rock sprites, not freestanding gateways.
    rocks = (134, 132, 133, 135, 134)
    for xx in range(left + 1, right):
        obj[back][xx] = offset + rocks[(xx + variant) % len(rocks)]
    for xx in range(left, right + 1):
        obj[back + 1][xx] = offset + rocks[(xx + variant + 2) % len(rocks)]
    for xx in range(left, right + 1):
        obj[front][xx] = offset + rocks[(xx + variant + 1) % len(rocks)]
    obj[front][x], obj[front][x + 1] = offset + 226, offset + 227
    block(col, left, back, right - left + 1, front - back + 1)
    return (event(x, y, "activate=on_interact", "hotspot=location",
                  "tooltip=Dungeon Entrance", "script=scripts/town/enter_dungeon.txt", width=2) +
            event(x, y + 1, "intermap_id=dungeon_exit"))


def chunk(biome, role, variant):
    rng = random.Random(f"diantre-town-v1:{biome}:{role}:{variant}")
    bg = [[ground(biome, x, y) for x in range(SIZE)] for y in range(SIZE)]
    obj, col = grid(SIZE, 0), grid(SIZE, 0)
    extra = ""
    # Closed edges are opened only for the links chosen by the native generator.
    for y in range(SIZE):
        for x in range(SIZE):
            if min(x, y, SIZE-1-x, SIZE-1-y) < 2:
                col[y][x] = 1
                if x % 3 == 0 and y % 3 == 0:
                    obj[y][x] = rng.choice(BIOMES[biome].decorations)
    # Keep a broad, decoration-free cross: all four connectors are reachable.
    for y in range(2, SIZE-2):
        for x in range(2, SIZE-2):
            if 6 <= x <= 9 or 6 <= y <= 9:
                continue
            if rng.random() < BIOMES[biome].density:
                obj[y][x] = rng.choice(BIOMES[biome].decorations)
                block(col, x, y)
    if biome in ("swamp", "coast"):
        # A water pocket is outside the protected crossing; the routes stay dry.
        pond = [[144, 176, 177, 146], [148, 180, 181, 150],
                [148, 180, 181, 150], [155, 159, 160, 153]]
        corners = [(2, 2), (10, 2), (2, 10), (10, 10)]
        pockets = corners if biome == "coast" else [(10, 10) if role == "start" else rng.choice(corners)]
        for px, py in pockets:
            for y, row in enumerate(pond, py):
                for x, tile in enumerate(row, px):
                    bg[y][x], obj[y][x], col[y][x] = tile, 0, 1
    if role == "links":
        # Only these strips are copied onto an actually connected chunk edge.
        obj, col = grid(SIZE, 0), grid(SIZE, 0)
        for x, y, w, h, direction in [(6, 0, 4, 8, "north"), (6, 8, 4, 8, "south"),
                                       (0, 6, 8, 4, "west"), (8, 6, 8, 4, "east")]:
            extra += event(x, y, f"procgen_link={direction}", width=w, height=h)
    elif role == "start" or (role == "normal" and variant in (0, 4)):
        # A large ruined house from the grassland atlas, with a matching footprint.
        for y in range(2, 7):
            for x in range(2, 6):
                obj[y][x] = 0
        # Anchors must stay outside both the horizontal and vertical link strips.
        obj[5][2] = BIOMES[biome].house
        block(col, 2, 1, 4, 5)
        if role == "start":
            # Exactly one market/service hub: this chunk is generated once.
            extra += ("\n[npc]\ntype=npc\nlocation=5,9,1,1\ndirection=5\n"
                      "filename=npcs/town/provisions.txt\n"
                      "\n[npc]\ntype=npc\nlocation=10,8,1,1\ndirection=5\n"
                      "filename=npcs/town/smith.txt\n")
            obj[10][5], col[10][5] = 297, 0
            extra += event(5, 10, "activate=on_interact", "hotspot=location",
                           "stash=true", "tooltip=Shared Stash", "soundfx=soundfx/wood_open.ogg")
    elif role == "end":
        extra += dungeon_entrance(biome, variant, bg, obj, col)
    header = (f"[header]\nwidth={SIZE}\nheight={SIZE}\ntilewidth=192\ntileheight=96\n"
              "orientation=isometric\nhero_pos=8,10\n"
              f"procgen_type={role}\ntileset=tilesetdefs/town/palette.txt\n")
    # Cliff/water sprites have transparent sides. A continuous ground underlay
    # keeps those cutouts from exposing the renderer's black clear colour.
    underlay = [[ground(biome, x, y) for x in range(SIZE)] for y in range(SIZE)]
    return (header + layer("background_base", underlay) + layer("background", bg) +
            layer("object", obj) + layer("collision", col) + extra)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tilesets", type=Path, default=ROOT.parents[1] / "mods/diantre/tilesetdefs")
    args = parser.parse_args()
    palette = "INCLUDE tilesetdefs/tileset_grassland.txt\n"
    for name, offset in [("snowplains", 1000), ("cave", 2000), ("ruins", 3000), ("dungeon", 4000)]:
        source = args.tilesets / f"tileset_{name}.txt"
        if not source.is_file():
            source = ROOT.parents[1] / "mods/diantre/tilesetdefs" / source.name
        lines = [f"# Flare {source.name}; tile IDs offset by {offset} to share the palette."]
        for line in source.read_text().splitlines():
            if line.startswith("tile="):
                key, rest = line.split(",", 1)
                line = f"tile={int(key[5:]) + offset}," + rest
            elif line.startswith("animation="):
                key, rest = line.split(";", 1)
                line = f"animation={int(key[10:]) + offset};" + rest
            lines.append(line)
        write(f"tilesetdefs/town/{name}.txt", "\n".join(lines) + "\n")
        palette += f"INCLUDE tilesetdefs/town/{name}.txt\n"
    write("tilesetdefs/town/palette.txt", palette)
    for biome, spec in BIOMES.items():
        title, decorations = spec.title, spec.decorations
        bg = [[ground(biome, x, y) for x in range(WORLD)] for y in range(WORLD)]
        obj, col = grid(WORLD, 0), grid(WORLD, 1)
        rng = random.Random("town-border:" + biome)
        for y in range(0, WORLD, 3):
            for x in range(0, WORLD, 3):
                obj[y][x] = rng.choice(decorations)
        text = (f"[header]\nwidth={WORLD}\nheight={WORLD}\ntilewidth=192\ntileheight=96\n"
                "orientation=isometric\nhero_pos=8,10\n"
                f"title={title}\nmusic=music/town_theme.ogg\n"
                "tileset=tilesetdefs/town/palette.txt\n")
        text += layer("background_base", bg) + layer("background", bg) + layer("object", obj) + layer("collision", col)
        text += event(0, 0, f"procgen_filename=maps/town/rules/{biome}.txt", width=REGION, height=REGION)
        text += event(0, 0, "activate=on_load", f"set_status=diantre_town_{biome}",
                       "unset_status=" + ",".join("diantre_town_"+b for b in BIOMES if b != biome))
        write(f"maps/town/{biome}.txt", text)
        rules = ("[settings]\ndoors_max=0\nmain_path_length_min=5\nmain_path_length_max=9\n"
                 "main_path_attempts_max=1000\nbranch_length_min=2\nbranch_length_max=4\n"
                 "branches_per_door_level_max=2\n\n[chunks]\n")
        for role, count in [("links", 1), ("start", 2), ("end", 3), ("normal", 8)]:
            for variant in range(count):
                name = f"maps/town/chunks/{biome}/{role}_{variant}.txt"
                write(name, chunk(biome, role, variant))
                rules += f"filename={name}\n"
        write(f"maps/town/rules/{biome}.txt", rules)
    write("maps/town/biomes.txt", "".join(f"map=maps/town/{b}.txt\n" for b in BIOMES))
    write("scripts/town/return.txt", "".join(
        f"[event]\nrequires_status=diantre_town_{b}\nintermap=maps/town/{b}.txt,-1,-1,dungeon_exit\n\n"
        for b in BIOMES) + "[event]\nrequires_not_status=" + ",".join(
            "diantre_town_"+b for b in BIOMES) + "\nintermap_random=maps/town/biomes.txt\n")
    write("scripts/town/enter_dungeon.txt", "[event]\nset_status=emp_il_f1\n"
          "intermap=maps/iron_labyrinth_f1.txt\nsoundfx=soundfx/environment/stairs.ogg\n")
    write("npcs/town/provisions.txt", "name=Lysa, Provisions\n"
          "animations=animations/npcs/peasant_woman1.txt\ndirection=5\nvendor=true\ntalker=false\n"
          "constant_stock=2:20,3:20,1105:5\n")
    write("npcs/town/smith.txt", "name=Borin, Equipment\n"
          "animations=animations/npcs/knight.txt\ndirection=5\nvendor=true\ntalker=false\n"
          "random_stock=loot/il_loren.txt\nrandom_stock_count=5,8\n")
    print(f"Built {len(BIOMES)} town biomes and their reusable native-procgen chunks.")


if __name__ == "__main__":
    main()
