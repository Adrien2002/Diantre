#!/usr/bin/env python3
"""Compact the checked-in native rooms without changing their encounters/events.

The original modules are 48x48, including a six-cell rock margin. Removing
that margin keeps the authored round rooms, vaults, doors and keys, while
bringing neighbouring rooms up to a shared boundary. Safe to run again.
"""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1] / "diantre"
SIZE, MARGIN = 36, 6


def compact(path):
    text = path.read_text()
    if "width=36\n" in text:
        return
    assert "width=48\n" in text, path
    blocks = re.split(r"\n(?=\[)", text)
    result = []
    is_link = "procgen_type=links\n" in text
    for block in blocks:
        if block.startswith("[layer]"):
            prefix, raw = block.split("data=\n", 1)
            rows = [[int(v) for v in l.split(",")] for l in raw.splitlines() if l.strip()]
            rows = [r[MARGIN:-MARGIN] for r in rows[MARGIN:-MARGIN]]
            result.append(prefix + "data=\n" + "\n".join(",".join(map(str, r)) for r in rows) + "\n")
            continue
        lines = block.splitlines()
        converted = []
        for line in lines:
            if line in ("width=48", "height=48"):
                line = line.split("=")[0] + f"={SIZE}"
            elif line.startswith("hero_pos="):
                x, y = map(int, line.split("=")[1].split(","))
                line = f"hero_pos={x-MARGIN},{y-MARGIN}"
            elif line.startswith("location="):
                x, y, w, h = map(int, line.split("=")[1].split(","))
                xx, yy = max(x, MARGIN), max(y, MARGIN)
                ww, hh = min(x+w, 48-MARGIN)-xx, min(y+h, 48-MARGIN)-yy
                if ww <= 0 or hh <= 0:
                    # on_load sentinels have no spatial meaning.
                    assert "activate=on_load" in lines, (path, line)
                    line = "location=0,0,1,1"
                else:
                    line = f"location={xx-MARGIN},{yy-MARGIN},{ww},{hh}"
            elif line.startswith("mapmod="):
                mods = []
                for part in line.split("=", 1)[1].split(";"):
                    layer, x, y, tile = part.split(",")
                    x, y = int(x)-MARGIN, int(y)-MARGIN
                    assert 0 <= x < SIZE and 0 <= y < SIZE, (path, part)
                    mods.append(f"{layer},{x},{y},{tile}")
                line = "mapmod=" + ";".join(mods)
            converted.append(line)
        result.append("\n".join(converted).rstrip()+"\n")
    if not is_link:
        # Unconnected boundaries stay sealed; only native link overlays open
        # them. Otherwise touching rooms could bypass a locked door level.
        collision = next(b for b in result if b.startswith("[layer]\ntype=collision"))
        objects = next(b for b in result if b.startswith("[layer]\ntype=object"))
        c = [[int(v) for v in r.split(",")] for r in collision.split("data=\n")[1].splitlines()]
        o = [[int(v) for v in r.split(",")] for r in objects.split("data=\n")[1].splitlines()]
        for y in range(SIZE):
            for x in range(SIZE):
                if (x in (0,SIZE-1) or y in (0,SIZE-1)) and c[y][x] == 0:
                    c[y][x], o[y][x] = 1, 144
        for old, data in ((collision,c),(objects,o)):
            result[result.index(old)] = old.split("data=\n")[0]+"data=\n"+"\n".join(",".join(map(str,r)) for r in data)+"\n"
    path.write_text("\n".join(result).rstrip()+"\n")


def compact_floor(path):
    text = path.read_text()
    if "width=160\n" in text:
        return
    assert "width=208\n" in text, path
    parts = re.split(r"\n(?=\[)", text)
    for i, part in enumerate(parts):
        if part.startswith("[layer]"):
            prefix, _ = part.split("data=\n",1)
            value = 3 if "type=collision\n" in prefix else 0
            row = ",".join([str(value)]*160)
            parts[i] = prefix+"data=\n"+"\n".join([row]*160)+"\n"
        else:
            parts[i] = part.replace("width=208", "width=160").replace("height=208", "height=160").replace("hero_pos=24,24", "hero_pos=18,18").replace("location=0,0,192,192", "location=0,0,144,144")
    path.write_text("\n".join(parts).rstrip()+"\n")


def main():
    # The native 'complete block' has textured masonry on both visible faces.
    # Other wall orientations contain opaque black rear faces, inappropriate
    # for these freestanding generated boundaries. No atlas pixels are edited.
    palette = ROOT / "tilesetdefs/tileset_ruins.txt"
    lines = palette.read_text().splitlines()
    complete = next(l.split("=",1)[1].split(",")[1:] for l in lines if l.startswith("tile=144,"))
    for i, line in enumerate(lines):
        if line.startswith("tile=") and 136 <= int(line[5:].split(",")[0]) <= 151:
            lines[i] = "tile="+",".join([line[5:].split(",")[0],*complete])
    palette.write_text("\n".join(lines)+"\n")
    paths = sorted((ROOT / "maps/iron_labyrinth/generated").rglob("*.txt"))
    for path in paths:
        compact(path)
    for floor in range(1,4):
        path = ROOT / f"maps/iron_labyrinth_f{floor}.txt"
        compact_floor(path)
        paths.append(path)
    paths.append(palette)
    manifest_path = ROOT / "ASSET_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    for path in paths:
        key = path.relative_to(ROOT).as_posix()
        record = manifest["files"][key]
        data = path.read_bytes()
        record.update(sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
        note = "Diantre 0.5.1: compact adjoining room modules and fully textured wall blocks; native atlas unchanged."
        if note not in record["changes"]:
            record["changes"].append(note)
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")


if __name__ == "__main__":
    main()
