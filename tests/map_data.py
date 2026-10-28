"""Small reader for the actual map/save files emitted by Flare."""
from collections import deque
import re


def sections(text):
    result = []
    current = None
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("["):
            current = {"section": line.strip("[]")}
            result.append(current)
        elif current is not None and "=" in line:
            key, value = line.split("=", 1)
            # MapSaver writes one line per component, even when the source
            # used a semicolon-separated list on a single line.
            if key == "mapmod" and key in current:
                current[key] += ";" + value
            else:
                current[key] = value
            if key == "data":
                current[key] = []
        elif current is not None and isinstance(current.get("data"), list):
            current["data"].append([int(x) for x in line.split(",") if x])
    return result


def connected(collision, start):
    pending = deque([start])
    seen = {start}
    while pending:
        x, y = pending.popleft()
        for nx, ny in [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]:
            if (0 <= ny < len(collision) and 0 <= nx < len(collision[ny]) and
                    collision[ny][nx] == 0 and (nx, ny) not in seen):
                seen.add((nx, ny))
                pending.append((nx, ny))
    return seen


def surface_layers(data):
    """Read generated tiles, then apply the town's native on-load mapmods."""
    layers = {s["type"]: [row[:] for row in s["data"]]
              for s in data if s["section"] == "layer"}
    for entry in data:
        if entry.get("activate") == "on_load" and "mapmod" in entry:
            assert not any(key.startswith("requires") for key in entry), entry
            for modification in entry["mapmod"].split(";"):
                name, x, y, tile = modification.split(",")
                layers[name][int(y)][int(x)] = int(tile)
    return layers


def check_open_square(layers, start):
    """A shared open plaza, broad approaches, and a complete outer backdrop."""
    collision = layers["collision"]
    reachable = connected(collision, start)
    low, high = 17, 64
    width = high-low
    assert len(reachable) > width*width*0.88, "Town is divided into small clearings"
    assert all(low <= x < high and low <= y < high for x, y in reachable), "Open town perimeter"
    for y in range(28, 49):
        for x in range(28, 49):
            assert collision[y][x] == layers["object"][y][x] == 0, "Obstructed central plaza"
    for i in range(low, high):
        assert sum(collision[i][x] == 0 for x in range(low, high)) >= width*0.5, ("Narrow town row", i)
        assert sum(collision[y][i] == 0 for y in range(low, high)) >= width*0.5, ("Narrow town column", i)
    # Cover the largest supported test viewport at every accessible position.
    extent = 3440/384 + 1440/192
    height, width = len(collision), len(collision[0])
    assert all(extent <= x+0.5 < width-extent and extent <= y+0.5 < height-extent
               for x, y in reachable), "Surface reaches the map canvas edge"
    return reachable


def town_details(path):
    text = path.read_text()
    data = sections(text)
    header = next(d for d in data if d["section"] == "header")
    layers = surface_layers(data)
    collision = layers["collision"]
    entrances = [d for d in data if d.get("script") == "scripts/town/enter_dungeon.txt"]
    assert len(entrances) == 1, (path, "Must have exactly one dungeon entrance")
    start = tuple(map(int, header["hero_pos"].split(",")))
    door = tuple(map(int, entrances[0]["location"].split(",")[:2]))
    assert collision[start[1]][start[0]] == 0, (path, "Blocked hero spawn")
    reachable = check_open_square(layers, start)
    assert door in reachable, (path, "Dungeon entrance not reachable from town arrival")
    npcs = [d for d in data if d["section"] == "npc"]
    expected = {f"npcs/town/{name}.txt" for name in
                ("udana", "florin", "yora", "abasi", "bakat", "martigan", "loren")}
    assert len(npcs) == 7, (path, "Must have exactly seven town vendors")
    assert {npc["filename"] for npc in npcs} == expected, (path, "Missing or duplicate merchant")
    houses = {(x, y) for y, row in enumerate(layers["object"])
              for x, tile in enumerate(row) if tile in (296, 1744)}
    assert len(houses) == 7, (path, "Each vendor needs a separate house")
    for npc in npcs:
        pos = tuple(map(int, npc["location"].split(",")[:2]))
        assert pos in reachable, (path, "Inaccessible vendor", pos)
        assert (pos[0]-3, pos[1]-2) in houses, (path, "Vendor has no house", pos)
    assert len([d for d in data if d.get("stash") in ("true", "1")]) == 1
    assert not [d for d in data if d["section"] == "enemy"], "Town must be safe"
    exit_point = next(d for d in data if d.get("intermap_id") == "dungeon_exit")
    # Every shop and the cave return must connect to the plaza through a route
    # at least three tiles wide, rather than just a one-tile forest passage.
    height, width = len(collision), len(collision[0])
    broad = [[1]*width for _ in range(height)]
    for y in range(1, height-1):
        for x in range(1, width-1):
            if all(collision[yy][xx] == 0 for yy in range(y-1, y+2) for xx in range(x-1, x+2)):
                broad[y][x] = 0
    approaches = connected(broad, (38, 38))
    for entry in [*npcs, exit_point]:
        pos = tuple(map(int, entry["location"].split(",")[:2]))
        assert pos in approaches, (path, "Narrow approach to merchant or dungeon", pos)
    return {"header": header, "entrance": door, "npcs": npcs,
            "exit": tuple(map(int, exit_point["location"].split(",")[:2]))}
