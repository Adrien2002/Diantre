#!/usr/bin/env python3
"""Guard per-character procedural cache initialization and chunk-status cleanup."""
from pathlib import Path
import json
from check_surface import parse
from build_exploration import FAMILIES, stable_status

ROOT=Path(__file__).resolve().parents[1]/"diantre"
def get_sections(path):
    return parse(ROOT/path)
def events(sections):
    return [s for s in sections if s["section"]=="event"]

def main():
    spawn=events(get_sections("maps/spawn.txt"))
    saves=[e for e in spawn if e.get("activate")=="on_load" and e.get("save_game")=="true"]
    teleports=[e for e in spawn if e.get("intermap_random")=="maps/town/biomes.txt"]
    assert len(saves)==len(teleports)==1
    assert teleports[0].get("activate")=="on_load"
    assert teleports[0].get("delay")=="350ms", "Startup must save before entering procedural map"
    enter=events(get_sections("scripts/town/enter_dungeon.txt"))
    assert any(s.get("save_game")=="true" for s in enter)
    assert any(s.get("delay")=="250ms" and s.get("intermap")=="maps/iron_labyrinth_f1.txt" for s in enter)
    town=events(get_sections("maps/town/hamlet_forest.txt"))
    statuses="diantre_compact_normal_a,diantre_compact_normal_b"
    assert {x.get("activate") for x in town if x.get("unset_status")==statuses}=={"on_load","on_mapexit"}
    for file in ("scripts/town/return.txt","scripts/town/return_waypoint.txt"):
        ev=events(get_sections(file))
        assert ev[0].get("unset_status")==statuses,(file,"Merchant selection not reset before return")
    for floor in range(1,4):
        ev=events(get_sections(f"maps/iron_labyrinth_f{floor}.txt"))
        cleanup=[e for e in ev if e.get("type")=="diantre_chunk_selection_cleanup"]
        assert {e["activate"] for e in cleanup}=={"on_load","on_mapexit"},(floor,"Missing cleanup")
        expected={stable_status(f"diantre_f{floor}_complex_{family}"+
                                (f"_{i}" if family!="vault" else ""))
                  for family in FAMILIES for i in range(4)}
        for e in cleanup:
            assert set(e["unset_status"].split(","))==expected,(floor,"Cleanup misses a chunk")
        assert not any("procgen_reset_status" in e for e in ev),(floor,"Unrequested reroll")
    print(json.dumps({"startup_cache_delay_ms":350,"dungeon_entry_delay_ms":250,
                      "town_pre_return_status_reset":True,"town_exit_status_reset":True,
                      "floor_chunk_status_reset":True,"per_character_save_prefix":(
                          (ROOT/"engine/misc.txt").read_text().splitlines()[-1]=="save_prefix=diantre")},
                     indent=2))

if __name__=="__main__":
    main()
