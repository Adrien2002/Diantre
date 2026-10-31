#!/usr/bin/env python3
"""Verify stock-Flare waypoint NPCs, travel status gates and arrival points."""
from pathlib import Path
import json
from check_surface import parse, layers, reachable

ROOT=Path(__file__).resolve().parents[1]/"diantre"
UNLOCK="diantre_waypoint_f2"

def dialogs(path):
    raw=(ROOT/path).read_text()
    groups=[]
    for block in raw.split("[dialog]")[1:]:
        props={}
        for line in block.splitlines():
            if not line or line.startswith("#") or "=" not in line:
                continue
            key,value=line.split("=",1)
            if key=="response":
                props.setdefault("responses",[]).append(value)
            else:
                assert key not in props,(path,key)
                props[key]=value
        groups.append(props)
    return groups

def inspect_menu(path,has_town):
    raw=(ROOT/path).read_text()
    assert "animations=animations/npcs/return_obelisk1.txt" in raw
    assert "talker=true" in raw
    nodes=dialogs(path)
    main=[n for n in nodes if not n.get("response_only")]
    assert len(main)==1 and main[0]["topic"]=="Travel",(path,main)
    targets={n["id"]:n for n in nodes if n.get("response_only")=="true"}
    expected={"floor_1","floor_2","cancel"}|({"town"} if has_town else set())
    assert set(main[0]["responses"])==set(targets)==expected,(path,targets)
    assert targets["floor_2"]["requires_status"]==UNLOCK,(path,"Ungated level 2")
    assert targets["floor_2"]["intermap"]=="maps/iron_labyrinth_f2.txt,-1,-1,diantre_waypoint_f2"
    assert targets["floor_1"]["intermap"]=="maps/iron_labyrinth_f1.txt,-1,-1,stairs_up"
    assert not any("requires_status" in targets[n] for n in ("floor_1","cancel"))
    if has_town:
        assert targets["town"]["script"]=="scripts/town/return_waypoint.txt"
        assert main[0]["set_status"]==UNLOCK
        assert main[0]["save_game"]=="true"
    else:
        assert "set_status" not in main[0]
    assert targets["cancel"]["topic"]=="Cancel"
    return len(nodes)

def main():
    town=parse(ROOT/"maps/town/hamlet_forest.txt")
    start=parse(ROOT/"maps/iron_labyrinth/exploration/f2/start.txt")
    tdata=layers(town);sdata=layers(start)
    def check_events(sections,portal,trigger,landing,npcfile):
        anchors=[s for s in sections if s["section"]=="npc" and s.get("filename")==npcfile]
        assert len(anchors)==1,(npcfile,"NPC absent or duplicated")
        assert tuple(map(int,anchors[0]["location"].split(",")[:2]))==portal
        triggers=[s for s in sections if s["section"]=="event" and s.get("npc")==npcfile]
        assert len(triggers)==1
        event=triggers[0]
        assert event.get("activate")=="on_trigger"
        assert tuple(map(int,event["location"].split(",")[:2]))==trigger
        assert event.get("repeat")=="true"
        c=layers(sections)["collision"]
        for x,y in (portal,trigger,landing):
            assert c[y][x]==0,(npcfile,"Blocked waypoint tile",(x,y))
            assert layers(sections)["object"][y][x]==0,(npcfile,"Occluded waypoint tile",(x,y))
        assert trigger in reachable(c,landing),(npcfile,"No access to portal")
        return event
    town_event=check_events(town,(9,14),(9,15),(10,15),"npcs/diantre_waypoint_town.txt")
    start_event=check_events(start,(23,20),(23,21),(22,21),"npcs/diantre_waypoint_f2.txt")
    assert UNLOCK not in str(town_event), "Town must not unlock unvisited floor"
    assert start_event.get("set_status")==UNLOCK and start_event.get("save_game")=="true"
    for path,ref in [("maps/town/hamlet_forest.txt","diantre_waypoint_town"),
                     ("maps/iron_labyrinth/exploration/f2/start.txt","diantre_waypoint_f2")]:
        sec=town if "hamlet" in path else start
        ids=[s for s in sec if s["section"]=="event" and s.get("intermap_id")==ref]
        assert len(ids)==1,(path,ref)
    for floor in (1,3):
        other=parse(ROOT/f"maps/iron_labyrinth/exploration/f{floor}/start.txt")
        assert not any(s.get("filename")=="npcs/diantre_waypoint_f2.txt" for s in other)
    n1=inspect_menu("npcs/diantre_waypoint_town.txt",False)
    n2=inspect_menu("npcs/diantre_waypoint_f2.txt",True)
    ret=(ROOT/"scripts/town/return_waypoint.txt").read_text()
    assert "requires_status=diantre_town_hamlet_forest\nintermap=maps/town/hamlet_forest.txt,-1,-1,diantre_waypoint_town" in ret
    assert ret.count("intermap=")==(ROOT/"scripts/town/return.txt").read_text().count("intermap=")
    print(json.dumps(dict(waypoints=2,unlocked_floors=[1,2],initially_available=[1],
                          unlock_status=UNLOCK,menu_nodes=[n1,n2],
                          native_animations=True,persistent_activation=True),indent=2))

if __name__=="__main__":
    main()
