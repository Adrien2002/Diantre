#!/usr/bin/env python3
"""Check native room seams, sealed boundaries, event coordinates and gates."""
from pathlib import Path
from itertools import product
import copy
import json

from check_surface import parse, layers, reachable

ROOT = Path(__file__).resolve().parents[1] / "diantre"
SIDES = ("north", "south", "west", "east")
PORTS = ((18,0), (18,35), (0,18), (35,18))


def mapmods(sections, collision):
    for section in sections:
        for mod in section["mapmods"]:
            layer, x, y, tile = mod.split(",")
            if layer == "collision":
                collision[int(y)][int(x)] = int(tile)


def main():
    templates = seams = gates = 0
    for floor in range(1,4):
        folder = ROOT / f"maps/iron_labyrinth/generated/f{floor}"
        maps = {p.stem: parse(p) for p in folder.glob("*.txt")}
        links = [maps[f"links_{i}"] for i in range(3)]
        rects = {s["procgen_link"]: tuple(map(int,s["location"].split(",")))
                 for s in links[0] if "procgen_link" in s}
        statuses = []
        for name, sections in maps.items():
            header = next(s for s in sections if s["section"] == "header")
            assert header["width"] == header["height"] == "36", name
            data = layers(sections)
            assert list(data) == ["background", "background_fringe", "object", "collision"]
            assert all(len(rows)==36 and all(len(r)==36 for r in rows) for rows in data.values())
            for s in sections:
                if "location" in s:
                    x,y,w,h = map(int,s["location"].split(","))
                    assert 0<=x<x+w<=36 and 0<=y<y+h<=36, (name,s)
                for mod in s["mapmods"]:
                    _,x,y,_ = mod.split(",")
                    assert 0<=int(x)<36 and 0<=int(y)<36, (name,mod)
            if name.startswith("links"):
                continue
            templates += 1
            c = data["collision"]
            assert all(c[0][i] and c[35][i] and c[i][0] and c[i][35] for i in range(36)), (name,"unlinked room leaks")
            kind = header["procgen_type"]
            if kind == "key":
                statuses.append(header["procgen_unique_status"])
                assert any(s.get("tooltip")=="Vault Lever" for s in sections)
            masks = [(True,True,False,False)] if kind=="door_north_south" else [(False,False,True,True)] if kind=="door_west_east" else product((False,True),repeat=4)
            for mask in masks:
                if not any(mask):
                    continue
                for link in links:
                    merged = copy.deepcopy(c)
                    for side,enabled in zip(SIDES,mask):
                        if enabled:
                            x,y,w,h = rects[side]
                            for yy in range(y,y+h):
                                merged[yy][x:x+w] = layers(link)["collision"][yy][x:x+w]
                    ports = [p for p,on in zip(PORTS,mask) if on]
                    assert all(merged[y][x]==0 for x,y in ports), (name,mask,"closed seam")
                    if kind.startswith("door_"):
                        assert ports[1] not in reachable(merged,ports[0]), (name,"locked gate bypass")
                        gates += 1
                    # Opening all local doors must connect every selected port.
                    mapmods(sections,merged)
                    seen = reachable(merged,ports[0])
                    assert all(p in seen for p in ports), (name,mask,"disconnected room")
                    # Chests/levers can be blocking props: their neighbours must
                    # be reachable, rather than the occupied cell itself.
                    for s in sections:
                        if s.get("tooltip") in ("Vault Lever","Key Chest","Treasure Chest"):
                            x,y,_,_=map(int,s["location"].split(","))
                            assert any((x+dx,y+dy) in seen for dx,dy in ((0,0),(1,0),(-1,0),(0,1),(0,-1))), (name,s.get("tooltip"),"unreachable interaction")
                    seams += 1
        assert len(statuses)==3 and len(set(statuses))==3, "Key-room states must be unique"
    print(json.dumps({"room_templates":templates,"link_combinations":seams,
                      "locked_gate_checks":gates,"checks":["sealed unused exits","connected selected exits","event coordinates","reachable interactions","no gate bypass"]},indent=2))


if __name__ == "__main__":
    main()
