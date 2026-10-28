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


def town_details(path):
    text = path.read_text()
    data = sections(text)
    header = next(d for d in data if d["section"] == "header")
    collision = next(d["data"] for d in data if d.get("type") == "collision")
    entrances = [d for d in data if d.get("script") == "scripts/town/enter_dungeon.txt"]
    assert len(entrances) == 1, (path, "Must have exactly one dungeon entrance")
    start = tuple(map(int, header["hero_pos"].split(",")))
    door = tuple(map(int, entrances[0]["location"].split(",")[:2]))
    assert collision[start[1]][start[0]] == 0, (path, "Blocked hero spawn")
    reachable = connected(collision, start)
    assert door in reachable, (path, "Dungeon entrance not reachable from town arrival")
    npcs = [d for d in data if d["section"] == "npc"]
    assert len(npcs) == 2, (path, "Must have exactly two town vendors")
    for npc in npcs:
        pos = tuple(map(int, npc["location"].split(",")[:2]))
        assert pos in reachable, (path, "Inaccessible vendor", pos)
    assert len([d for d in data if d.get("stash") in ("true", "1")]) == 1
    assert not [d for d in data if d["section"] == "enemy"], "Town must be safe"
    exit_point = next(d for d in data if d.get("intermap_id") == "dungeon_exit")
    return {"header": header, "entrance": door,
            "exit": tuple(map(int, exit_point["location"].split(",")[:2]))}
