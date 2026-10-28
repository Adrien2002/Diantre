#!/usr/bin/env python3
"""Author reusable surface chunks; Flare randomizes their layout in each save.

No Python runs while playing. Seeded Random below only makes the collection of
chunk variants reproducible. Flare selects the lots around one open town square.
"""
from pathlib import Path
import argparse
from dataclasses import dataclass
import random

ROOT = Path(__file__).resolve().parents[1] / "campaign/diantre"
SIZE = CHUNK_SIZE = 32
REGION = CHUNK_SIZE * 2
WORLD = REGION + 24
TOWN_MIN = 17
TOWN_MAX = 61  # Exclusive; the playable surface is one 44 by 44 square.
PLAZA_MIN = 28
PLAZA_MAX = 49  # Exclusive; no buildings or scenery occupy the central square.
VARIANTS = 3
CLIFF_CAP_OFFSET = 5000
CLIFF_TILE_BASE = 20000  # Earlier cached hills retain their original tile IDs.
CLIFF_JOIN_OFFSET = 20000
CLIFF_JOIN_FACES = (48, 49, 64, 65)
CLIFF_HEIGHT = 192
CLIFF_RISES = (CLIFF_HEIGHT * 2, 96, 96)


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


def cliff_layers(terraces, base_upper, expand=lambda values, kind: values):
    result = ""
    for level, (faces, tops) in enumerate(terraces):
        suffix = f"_{level + 1}" if level else ""
        result += layer("cliff_faces" + suffix, expand(faces, "terrain"))
        if not level:
            join = [[tile+CLIFF_JOIN_OFFSET if tile and tile%1000 in CLIFF_JOIN_FACES else 0
                     for tile in row] for row in base_upper]
            result += layer("cliff_faces_join", expand(join, "terrain"))
            result += layer("cliff_faces_upper", expand(base_upper, "terrain"))
        result += layer("cliff_tops" + suffix, expand(tops, "terrain"))
    return result


def dungeon_entrance(biome, variant, bg, terraces, base_upper, obj, col):
    # The native generator places this lot in a randomly selected town corner.
    x, y = [(20, 22), (19, 23), (20, 23)][variant]
    left, right, back, front = 17, 22, 17, y - 1
    offset = 1000 if biome == "snow" else 0
    # The entrance faces an open approach, away from foreground tree canopies.
    for yy in range(16, 31):
        for xx in range(16, 31):
            obj[yy][xx], col[yy][xx] = 0, 0
            bg[yy][xx] = ground(biome, xx, yy)
    # Successively narrower terraces recede behind the cave. Shorter upper
    # risers form a hillside. Two stacked wall sections at the base keep the
    # cave arch below the terrain lip, without an intermediate grass ledge.
    # Every terrain level renders before the mouth, keeping the arch visible.
    profiles = [(right, front), (right - 1, front - 2), (right - 2, front - 3)]
    for level, ((edge, lip), (faces, tops)) in enumerate(zip(profiles, terraces)):
        band = CLIFF_TILE_BASE + CLIFF_CAP_OFFSET * (level + 1)
        for yy in range(back, lip + 1):
            for xx in range(left, edge + 1):
                if yy == back:
                    tile = 66 if xx == left else 67 if xx == edge else 51
                elif yy == lip:
                    tile = 65 if xx == left else 64 if xx == edge else 49
                elif xx == left:
                    tile = 50
                elif xx == edge:
                    tile = 48
                else:
                    tile = 0
                if tile:
                    faces[yy][xx] = offset + tile + (band if level else 0)
                    if not level:
                        base_upper[yy][xx] = band + offset + tile
                tops[yy][xx] = band + ground(biome, xx, yy)
    terraces[0][0][front][x:x + 2] = [0, 0]
    obj[front][x], obj[front][x + 1] = offset + 226, offset + 227
    block(col, left, back, right - left + 1, front - back + 1)
    return (event(x, y, "activate=on_interact", "hotspot=location",
                  "tooltip=Dungeon Entrance", "script=scripts/town/enter_dungeon.txt", width=2) +
            event(x, y+1, "intermap_id=dungeon_exit"))


def town_boundary(biome):
    """Restore the shared perimeter after native chunks overwrite the canvas.

    Flare's procgen ignores the region's X/Y offset. Keep its lots seamless and
    enforce just the outer town boundary with native on-load map modifications.
    These events are saved with the generated map and reapplied on every visit.
    """
    changes = []
    for y in range(WORLD):
        for x in range(WORLD):
            if ((x in (TOWN_MIN-1, TOWN_MAX) and TOWN_MIN-1 <= y <= TOWN_MAX) or
                    (y in (TOWN_MIN-1, TOWN_MAX) and TOWN_MIN-1 <= x <= TOWN_MAX)):
                changes.append(f"collision,{x},{y},1")
            if x % 3 == 0 and y % 3 == 0 and not (
                    TOWN_MIN-2 <= x < TOWN_MAX+2 and TOWN_MIN-2 <= y < TOWN_MAX+2):
                tile = random.Random(f"town-edge:{biome}:{x}:{y}").choice(BIOMES[biome].decorations)
                changes.append(f"object,{x},{y},{tile}")
    for y in range(PLAZA_MIN, PLAZA_MAX):
        for x in range(PLAZA_MIN, PLAZA_MAX):
            changes.extend((f"object,{x},{y},0", f"collision,{x},{y},0"))
    return event(0, 0, "activate=on_load", "mapmod=" + ";".join(changes))


def house(biome, variant, obj, col):
    x, y = [(17, 22), (19, 23), (18, 24)][variant]
    # Leave a generous yard around each building so it reads as a town lot.
    for yy in range(16, 31):
        for xx in range(16, 31):
            obj[yy][xx], col[yy][xx] = 0, 0
    obj[y][x] = BIOMES[biome].house
    block(col, x, y-4, 4, 5)
    return x+3, y+2


def chunk(biome, role, variant):
    rng = random.Random(f"diantre-open-town:{biome}:{role}:{variant}")
    bg = [[ground(biome, x, y) for x in range(SIZE)] for y in range(SIZE)]
    obj, col = grid(SIZE, 0), grid(SIZE, 0)
    terraces = [(grid(SIZE, 0), grid(SIZE, 0)) for _ in CLIFF_RISES]
    base_upper = grid(SIZE, 0)
    extra = ""
    # Scattered props never form walls between lots. The central plaza and the
    # outer forest belt are shared across the entire surface, not per chunk.
    for y in range(2, SIZE-1, 4):
        for x in range(2, SIZE-1, 4):
            if rng.random() < BIOMES[biome].density * 2:
                obj[y][x] = rng.choice(BIOMES[biome].decorations)
                col[y][x] = 1
    if role == "links":
        obj, col = grid(SIZE, 0), grid(SIZE, 0)
        # Native graph links are metadata here: the lots already share open
        # ground on every side. A harmless one-tile overlay satisfies Flare's
        # link copying without carving paths through the surface.
        for direction in ("north", "south", "west", "east"):
            extra += event(0, 0, f"procgen_link={direction}")
    elif role in ("start", "normal"):
        x, y = house(biome, variant, obj, col)
        vendor = "provisions" if role == "start" else "smith"
        extra += (f"\n[npc]\ntype=npc\nlocation={x},{y},1,1\ndirection=5\n"
                  f"filename=npcs/town/{vendor}.txt\n")
        if role == "start":
            obj[y+1][x+1] = 297
            extra += event(x+1, y+1, "activate=on_interact", "hotspot=location",
                           "stash=true", "tooltip=Shared Stash", "soundfx=soundfx/wood_open.ogg")
        if biome in ("swamp", "coast"):
            pond = [[152, 145, 145, 153], [144, 176, 177, 146],
                    [144, 180, 181, 146], [155, 147, 147, 154]]
            pockets = [(25, 18), (18, 27)] if biome == "coast" else [(25, 18)]
            for px, py in pockets:
                for yy, row in enumerate(pond, py):
                    for xx, tile in enumerate(row, px):
                        bg[yy][xx], obj[yy][xx], col[yy][xx] = tile, 0, 1
    elif role == "end":
        extra += dungeon_entrance(biome, variant, bg, terraces, base_upper, obj, col)
    header = (f"[header]\nwidth={CHUNK_SIZE}\nheight={CHUNK_SIZE}\ntilewidth=192\ntileheight=96\n"
              "orientation=isometric\nhero_pos=24,27\n"
              f"procgen_type={role}\ntileset=tilesetdefs/town/palette.txt\n")
    # Keep a continuous ground underlay beneath transparent water/cliff sprites.
    underlay = [[ground(biome, x, y) for x in range(SIZE)] for y in range(SIZE)]
    return (header + layer("background_base", underlay) + layer("background", bg) +
            cliff_layers(terraces, base_upper) + layer("object", obj) +
            layer("collision", col) + extra)


def cliff_palette(grassland):
    """Reuse atlas regions and offsets for terrain caps and shorter upper cliffs."""
    ground_tiles = {tile for spec in BIOMES.values() for tile in spec.ground_tiles}
    face_tiles = {tile + offset for offset in (0, 1000)
                  for tile in (48, 49, 50, 51, 64, 65, 66, 67)}
    wanted = ground_tiles | face_tiles
    found = set()
    lines = ["# Terraces reuse unchanged Empyrean atlases with raised or cropped tile regions."]
    sources = [grassland, *(ROOT / "tilesetdefs/town" / (name + ".txt")
                           for name in ("snowplains", "cave", "ruins", "dungeon"))]
    last_image = None
    for source in sources:
        for line in source.read_text().splitlines():
            if line.startswith("img="):
                image = line[4:]
            elif line.startswith("tile="):
                tile, *source_values = map(int, line[5:].split(","))
                if tile not in wanted:
                    continue
                if image != last_image:
                    lines.extend(["\n[tileset]", "img=" + image])
                    last_image = image
                elevation = 0
                for level, rise in enumerate(CLIFF_RISES):
                    values = source_values[:]
                    if tile in ground_tiles:
                        values[-1] += elevation + rise
                    elif level:
                        # Trim the top of the wall region, retaining its foot.
                        # The terrace above covers the cropped upper edge.
                        crop = CLIFF_HEIGHT - rise
                        values[1] += crop
                        values[3] -= crop
                        values[-1] += elevation - crop
                    else:
                        # A second full wall section extends the entrance
                        # cliff upward; both sections share one terrain cap.
                        values[-1] += CLIFF_HEIGHT
                    band = CLIFF_TILE_BASE + CLIFF_CAP_OFFSET * (level + 1)
                    lines.append("tile=" + ",".join(map(str, [band + tile, *values])))
                    if not level and tile%1000 in CLIFF_JOIN_FACES:
                        # Cover the lower wall's grass lip beneath the upper
                        # wall's irregular foot with its solid rock midsection.
                        join_values = source_values[:]
                        join_values[1] += CLIFF_HEIGHT // 2
                        join_values[3] = CLIFF_HEIGHT // 2
                        lines.append("tile=" + ",".join(map(str, [band+tile+CLIFF_JOIN_OFFSET, *join_values])))
                    elevation += rise
                found.add(tile)
    if found != wanted:
        raise ValueError(f"Missing plateau terrain tiles: {sorted(wanted - found)}")
    write("tilesetdefs/town/cliffs.txt", "\n".join(lines) + "\n")


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
    grassland = args.tilesets / "tileset_grassland.txt"
    if not grassland.is_file():
        grassland = ROOT.parents[1] / "mods/diantre/tilesetdefs/tileset_grassland.txt"
    cliff_palette(grassland)
    palette += "INCLUDE tilesetdefs/town/cliffs_legacy.txt\nINCLUDE tilesetdefs/town/cliffs.txt\n"
    write("tilesetdefs/town/palette.txt", palette)
    for biome, spec in BIOMES.items():
        title, decorations = spec.title, spec.decorations
        bg = [[ground(biome, x, y) for x in range(WORLD)] for y in range(WORLD)]
        obj = grid(WORLD, 0)
        col = [[int(not (TOWN_MIN <= x < TOWN_MAX and TOWN_MIN <= y < TOWN_MAX))
                for x in range(WORLD)] for y in range(WORLD)]
        rng = random.Random("town-border:" + biome)
        for y in range(0, WORLD, 3):
            for x in range(0, WORLD, 3):
                if col[y][x]:
                    obj[y][x] = rng.choice(decorations)
        text = (f"[header]\nwidth={WORLD}\nheight={WORLD}\ntilewidth=192\ntileheight=96\n"
                "orientation=isometric\nhero_pos=24,27\n"
                f"title={title}\nmusic=music/town_theme.ogg\n"
                "tileset=tilesetdefs/town/palette.txt\n")
        text += (layer("background_base", bg) + layer("background", bg) +
                 cliff_layers([(grid(WORLD, 0), grid(WORLD, 0)) for _ in CLIFF_RISES],
                              grid(WORLD, 0)) +
                 layer("object", obj) + layer("collision", col))
        text += event(0, 0, f"procgen_filename=maps/town/rules/{biome}.txt", width=REGION, height=REGION)
        text += town_boundary(biome)
        text += event(0, 0, "activate=on_load", f"set_status=diantre_town_{biome}",
                       "unset_status=" + ",".join("diantre_town_"+b for b in BIOMES if b != biome))
        write(f"maps/town/{biome}.txt", text)
        rules = ("[settings]\ndoors_max=0\nmain_path_length_min=3\nmain_path_length_max=3\n"
                 "main_path_attempts_max=1000\nbranch_length_min=0\nbranch_length_max=0\n"
                 "branches_per_door_level_max=0\n\n[chunks]\n")
        directory = ROOT / "maps/town/chunks" / biome
        if directory.exists():
            for path in directory.glob("*.txt"):
                path.unlink()
        for role, count in [("links", 1), ("start", VARIANTS), ("end", VARIANTS), ("normal", VARIANTS)]:
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
