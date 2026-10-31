#!/usr/bin/env python3
"""Build room complexes and persistent, stage-safe runtime loops for stock Flare.

Flare still builds its progression tree. Normal sectors advertise their door
level using invisible native tiles. The floor's on_load script (executed after
the copied sector events) can join two unused exits only when their levels
match. These random decisions are made by Flare once per floor and saved.
"""
from pathlib import Path
import hashlib
import json
import random
import re

from check_surface import parse, layers, reachable
from dungeon_themes import THEMES, write_palette, dress_layers, add_details

ROOT = Path(__file__).resolve().parents[1] / "diantre"
SIZE = 36
GRID = 4
LEVEL_TILE = 4096
PORT_TILE = 4100
LAYERS = ("background", "background_fringe", "object", "topology", "collision")
FAMILIES = ("cloister", "chambers", "grotto", "ring", "barracks", "forks", "vault", "gallery")
PORTS = ((18,7), (18,28), (7,18), (28,18))


def stable_status(label):
    # Flare hashes names with std::collate. Similar structured names can collide
    # across floors with libstdc++'s rotate/add hash. Add a deterministic nonce
    # and validate the complete status namespace before shipping the data.
    return "dx_"+hashlib.sha256(label.encode()).hexdigest()[:16]+"_"+label


def event(**values):
    return "[event]\n" + "\n".join(f"{k}={v}" for k,v in values.items()) + "\n"


def marker_events():
    return "\n".join(event(type="generation_marker", location="18,18,1,1",
        activate="on_load", procgen_door_level=level,
        mapmod=f"topology,18,18,{LEVEL_TILE+level}") for level in range(3))


class Complex:
    def __init__(self, floor, family, variant):
        self.floor, self.family, self.variant = floor, family, variant
        self.rng = random.Random(61000+floor*10000+FAMILIES.index(family)*100+variant)
        self.walk = set()
        self.events = []
        self.props = {}
        self.rooms = []
        self.reserved = set()
        self.prefix = f"diantre_f{floor}_complex_{family}_{variant}"
        self.theme = THEMES[floor]
        self.doors = []

    def carve(self, x, y):
        if 1 <= x < SIZE-1 and 1 <= y < SIZE-1 and (x,y) not in self.reserved:
            self.walk.add((x,y))

    def room(self, x1, y1, x2, y2, shape="rect"):
        cx, cy = (x1+x2)//2, (y1+y2)//2
        rx, ry = (x2-x1)/2+.5, (y2-y1)/2+.5
        for y in range(y1,y2+1):
            for x in range(x1,x2+1):
                distance=((x-cx)/rx)**2+((y-cy)/ry)**2
                limit=1
                if shape!='rect' and self.theme['id']=='caverns' and .7<distance<1.3:
                    limit+=self.rng.uniform(-.15,.15)
                if shape=="rect" or distance <= limit:
                    self.carve(x,y)
        self.rooms.append((cx,cy))
        return cx,cy

    def corridor(self, start, end, diagonal=False, width=1):
        x,y = start
        while True:
            for dy in range(-width,width+1):
                for dx in range(-width,width+1):
                    self.carve(x+dx,y+dy)
            if (x,y)==end:
                break
            if diagonal and x != end[0] and y != end[1]:
                x += 1 if end[0]>x else -1
                y += 1 if end[1]>y else -1
            elif x != end[0]:
                x += 1 if end[0]>x else -1
            else:
                y += 1 if end[1]>y else -1

    def architecture(self):
        r = self.rng
        if self.family=="vault":
            self.reserved = {(x,y) for y in range(25,34) for x in range(25,34)}
            shape='ellipse' if self.theme['id']=='caverns' else 'rect'
            self.room(4,4,14,14,shape)
            self.room(22,4,31,14,shape)
            self.room(4,22,15,31,shape)
            self.room(16,16,23,24)
        elif self.theme['id']=='caverns':
            self.cavern_rooms()
        elif self.theme['id']=='crypts':
            self.crypt_rooms()
        elif self.family=="cloister":
            self.room(5,5,30,30)
            ix,iy=11+r.randrange(3),11+r.randrange(3)
            iw,ih=10+r.randrange(3),10+r.randrange(3)
            self.walk.difference_update((x,y) for y in range(iy,iy+ih) for x in range(ix,ix+iw))
            self.room(3,11,10,22)
            self.room(25,11,32,22)
            self.rooms = [(8,8),(27,8),(8,27),(27,27)]
        elif self.family=="ring":
            self.room(2+r.randrange(3),2+r.randrange(3),32,32,"ellipse")
            ix,iy=12+r.randrange(3),12+r.randrange(3)
            iw,ih=8+r.randrange(3),8+r.randrange(3)
            self.walk.difference_update((x,y) for y in range(iy,iy+ih) for x in range(ix,ix+iw))
            self.rooms = [(18,8),(28,18),(18,28),(8,18)]
        elif self.family=="barracks":
            self.room(13,5,22,30)
            for y in (5,21):
                self.room(3,y,10,y+9)
                self.room(25,y,32,y+9)
        elif self.family=="gallery":
            self.room(3,4,22,15)
            self.room(13,20,32,31)
            self.room(25,4,32,13)
            self.room(3,23,10,31)
        else:
            for x,y in ((3,3),(21,3),(3,21),(21,21)):
                shiftx, shifty = r.randint(0,2),r.randint(0,2)
                self.room(x+shiftx,y+shifty,min(x+11+r.randint(-2,0),32),
                          min(y+11+r.randint(-2,0),32),
                          "ellipse" if self.family=="grotto" else "rect")
            if self.family=="chambers":
                self.room(13,12,22,24)
        connected = [self.rooms[0]]
        remaining = self.rooms[1:]
        edges=[]
        while remaining:
            a,b=min(((a,b) for a in connected for b in remaining),
                    key=lambda p:abs(p[0][0]-p[1][0])+abs(p[0][1]-p[1][1])+r.random()*5)
            edges.append((a,b));connected.append(b);remaining.remove(b)
        if self.family in ("grotto","gallery","chambers","forks") or self.theme['id']=='caverns':
            edges.append((self.rooms[-1],self.rooms[0]))
        if self.family not in ("ring","cloister") or self.theme['id']!='ruins':
            for a,b in edges:
                if self.theme['id']=='caverns':
                    self.tunnel(a,b)
                    continue
                elbow = (a[0],b[1]) if r.randrange(2) else (b[0],a[1])
                self.corridor(a,elbow,self.family in ("grotto","forks"))
                self.corridor(elbow,b,self.family in ("grotto","forks"))
        # Candidate exits stop at the link-overlay region. Unselected exits are
        # sealed by rock; Flare's normal links or a validated loop can open them.
        for port in PORTS:
            nearest=min(self.rooms,key=lambda p:abs(p[0]-port[0])+abs(p[1]-port[1]))
            if self.theme['id']=='caverns':self.tunnel(port,nearest)
            else:self.corridor(port,nearest,self.family=="grotto")
        if self.theme['id']=='caverns':
            # Discard any one-cell islands caused by ragged ellipse outlines.
            collision=[[0 if (x,y) in self.walk else 1 for x in range(SIZE)] for y in range(SIZE)]
            self.walk=reachable(collision,self.rooms[0])
        elif self.theme['id']=='crypts' and self.family in ('cloister','chambers','ring'):
            self.inner_chapel()
        for cx,cy in self.rooms[1::2]:
            p=cx-2,cy-2
            if all((p[0]+dx,p[1]+dy) in self.walk for dx in range(-2,3) for dy in range(-2,3)):
                self.props[p]=152
        if self.family=="vault":
            self.puzzle()
        else:
            p=self.rooms[-1]
            self.props[p]=264
            claimed=stable_status(self.prefix+"_treasure")
            self.events.append(event(type="event",location=f"{p[0]},{p[1]},1,1",
                activate="on_interact",hotspot="location",tooltip="Treasure Chest",
                loot="loot/il_chest_common.txt",loot_count="2,4",repeat="false",
                requires_not_status=claimed,set_status=claimed,
                mapmod=f"object,{p[0]},{p[1]},267",soundfx="soundfx/wood_open.ogg"))
            self.events.append(event(type="event",location=f"{p[0]},{p[1]},1,1",
                activate="on_load",requires_status=claimed,mapmod=f"object,{p[0]},{p[1]},267"))

    def cavern_rooms(self):
        r=self.rng
        if self.family in ('gallery','barracks'):
            self.room(3,15,32,20)
            for x,y in ((8,7),(26,7),(9,28),(27,28)):
                rx,ry=r.randint(4,6),r.randint(4,6)
                self.room(max(2,x-rx),max(2,y-ry),min(33,x+rx),min(33,y+ry),'ellipse')
        else:
            centers=[(9,9),(26,9),(9,26),(26,26)]
            if self.family in ('ring','cloister'):centers=[(18,8),(28,18),(18,28),(8,18)]
            if self.family in ('chambers','forks'):centers.append((18,18))
            for x,y in centers:
                x+=r.randint(-2,2);y+=r.randint(-2,2)
                rx,ry=r.randint(4,8),r.randint(4,8)
                self.room(max(2,x-rx),max(2,y-ry),min(33,x+rx),min(33,y+ry),'ellipse')

    def tunnel(self,start,end):
        x,y=start
        for _ in range(120):
            self.corridor((x,y),(x,y),width=1)
            if (x,y)==end:return
            if self.rng.random()<.2:
                dx,dy=self.rng.choice(((1,0),(-1,0),(0,1),(0,-1)))
            elif x!=end[0] and (y==end[1] or self.rng.random()<.5):dx,dy=(1 if end[0]>x else -1),0
            else:dx,dy=0,(1 if end[1]>y else -1)
            x=max(2,min(33,x+dx));y=max(2,min(33,y+dy))
        self.corridor((x,y),end,diagonal=True)

    def crypt_rooms(self):
        r=self.rng
        if self.family in ('cloister','chambers','ring'):
            self.room(3,3,32,32,'ellipse' if self.family=='ring' else 'rect')
            self.rooms=[(7,7),(28,7),(7,28),(28,28),(18,18)]
        else:
            self.room(13,3,22,32)
            for x,y in ((3,4),(24,4),(3,21),(24,21)):
                self.room(x,y,x+8,y+9+r.randrange(2),
                          'ellipse' if self.family=='grotto' else 'rect')
            if self.family=='forks':self.room(9,11,26,23)

    def inner_chapel(self):
        # An actual room enclosed within the larger hall. Its only entrance is
        # an ordinary persistent door, separate from progression keys.
        x1,x2=11+self.rng.randrange(2),24+self.rng.randrange(2)
        y1,y2=11+self.rng.randrange(2),24+self.rng.randrange(2)
        for y in range(y1,y2+1):
            for x in range(x1,x2+1):
                if x in (x1,x2) or y in (y1,y2):self.walk.discard((x,y))
        points=[(x,y1) for x in range(17,20)]
        self.walk.update(points);self.doors.append(points)

    def puzzle(self):
        # The optional vault never carries an exit, a progression key or stairs.
        # Both seal levers are reachable before opening this gate.
        for y in range(26,33):
            for x in range(26,33):self.walk.add((x,y))
        self.corridor((22,28),(24,28))
        self.corridor((22,28),(20,20))
        gate=((25,28),(25,29))
        self.props[gate[0]],self.props[gate[1]]=378,379
        opened=stable_status(self.prefix+"_open")
        changes=";".join(f"collision,{x},{y},0;object,{x},{y},0" for x,y in gate)
        self.events.append(event(type="event",location="25,28,1,2",activate="static",
            requires_status=stable_status(self.prefix+"_seal_a")+","+stable_status(self.prefix+"_seal_b"),
            requires_not_status=opened,mapmod=changes,set_status=opened,
            repeat="false",save_game="true",soundfx="soundfx/door_open.ogg"))
        self.events.append(event(type="event",location="25,28,1,2",activate="on_load",
            requires_status=opened,mapmod=changes))
        for label,p in zip(("a","b"),(self.rooms[0],self.rooms[1])):
            self.props[p]=272
            status=stable_status(self.prefix+"_seal_"+label)
            self.events.append(event(type="event",location=f"{p[0]},{p[1]},1,1",
                activate="on_interact",hotspot="location",tooltip="Vault Seal",
                requires_not_status=status,mapmod=f"object,{p[0]},{p[1]},273",
                set_status=status,save_game="true",repeat="false",
                msg="One of the two vault seals is released."))
            self.events.append(event(type="event",location=f"{p[0]},{p[1]},1,1",
                activate="on_load",requires_status=status,mapmod=f"object,{p[0]},{p[1]},273"))
        self.props[29,29]=264
        claimed=stable_status(self.prefix+"_treasure")
        self.events.append(event(type="event",location="29,29,1,1",activate="on_interact",
            hotspot="location",tooltip="Treasure Chest",requires_status=opened,
            requires_not_status=claimed,set_status=claimed,
            loot="loot/il_chest_common.txt",loot_count="2,4",repeat="false",
            mapmod="object,29,29,267",soundfx="soundfx/wood_open.ogg"))
        self.events.append(event(type="event",location="29,29,1,1",activate="on_load",
            requires_status=claimed,mapmod="object,29,29,267"))

    def build(self):
        self.architecture()
        data={n:[[0]*SIZE for _ in range(SIZE)] for n in LAYERS}
        for y in range(SIZE):
            for x in range(SIZE):
                if (x,y) in self.walk:
                    data["background"][y][x]=24+self.rng.randrange(8)
                    data["collision"][y][x]=0
                else:
                    adjacent=any((x+dx,y+dy) in self.walk for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)))
                    data["object"][y][x]=144 if adjacent else 153+self.rng.randrange(8)
                    data["collision"][y][x]=1 if adjacent else 3
        dress_layers(self.floor,data)
        for (x,y),tile in self.props.items():
            data["object"][y][x]=tile
            data["collision"][y][x]=1 if tile in (378,379) else 2
            if tile in (378,379):data["background"][y][x]=24
        if self.family in ("barracks","gallery","chambers") and not self.doors:
            candidates=[]
            for y in range(8,28):
                for x in range(8,28):
                    if (x,y) not in self.walk or (x,y) in self.props:continue
                    if all((xx,y) in self.walk for xx in range(x-1,x+2)) and all((xx,y) not in self.walk for xx in (x-2,x+2)):
                        if all((xx,yy) in self.walk for yy in (y-1,y+1) for xx in range(x-1,x+2)):
                            candidates.append((x,y))
            if candidates:
                x,y=self.rng.choice(candidates)
                self.doors.append([(xx,y) for xx in range(x-1,x+2)])
        for index,points in enumerate(self.doors):
            x,y=points[0]
            for xx,yy in points:
                data['background'][yy][xx]=24
                data['collision'][yy][xx]=1
                data['object'][yy][xx]=0
            data['object'][y][x]=376;data['object'][y][x+2]=377
            change=';'.join(f'collision,{xx},{yy},0;object,{xx},{yy},0' for xx,yy in points)
            status=stable_status(self.prefix+f'_door_{index}')
            self.events.append(event(type='event',location=f'{x},{y},3,1',activate='on_interact',
                hotspot='location',tooltip='Door',requires_not_status=status,mapmod=change,
                set_status=status,repeat='false',soundfx='soundfx/door_open.ogg'))
            self.events.append(event(type='event',location=f'{x},{y},3,1',activate='on_load',
                requires_status=status,mapmod=change))
        self.details=add_details(self,data)
        unique=stable_status(f"diantre_f{self.floor}_complex_{self.family}"+(f"_{self.variant}" if self.family!="vault" else ""))
        header=(f"[header]\nwidth={SIZE}\nheight={SIZE}\ntilewidth=192\ntileheight=96\n"
                f"orientation=isometric\ntileset={self.theme['palette']}\nhero_pos=18,18\n"
                f"procgen_type=normal\nprocgen_unique_status={unique}\n")
        self.events.append(marker_events())
        enemy=(f"[enemy]\ntype=enemy\nlocation=3,3,30,30\ncategory=diantre_depth_{self.floor}\n"
               "number=5,9\nspawn_level=default\n")
        return serialize(header,data,self.events+[enemy]),data


def serialize(header,data,events):
    parts=["# Generated by tools/build_exploration.py; edit the generator.\n",header]
    for name in LAYERS:
        parts.append(f"[layer]\ntype={name}\ndata=\n"+"\n".join(",".join(map(str,r)) for r in data[name])+"\n")
    return "\n".join(parts+events).rstrip()+"\n"


def install_copy(source,destination,floor):
    palette=THEMES[floor]['palette']
    text=source.read_text().replace("tileset=tilesetdefs/tileset_ruins.txt",f"tileset={palette}")
    sections=parse(source)
    blank="[layer]\ntype=topology\ndata=\n"+"\n".join([",".join(["0"]*SIZE)]*SIZE)+"\n\n"
    text=text.replace("[layer]\ntype=collision",blank+"[layer]\ntype=collision")
    kind=next(s for s in sections if s['section']=='header')["procgen_type"]
    if kind in ("normal","start","end"):text+="\n"+marker_events()
    if kind=="links":
        topo=[[0]*SIZE for _ in range(SIZE)]
        for x,y in ((18,0),(18,35),(0,18),(35,18)):topo[y][x]=PORT_TILE
        old="[layer]\ntype=topology\ndata=\n"+"\n".join([",".join(["0"]*SIZE)]*SIZE)
        new="[layer]\ntype=topology\ndata=\n"+"\n".join(",".join(map(str,r)) for r in topo)
        text=text.replace(old,new)
    # Use the shared serializer after adding metadata; preserve every original
    # event, enemy and link rectangle verbatim.
    destination.write_text(text.rstrip()+"\n")
    sections=parse(destination);data=layers(sections);dress_layers(floor,data)
    header=text.split('[layer]',1)[0].strip()
    other=[b for b in re.split(r'\n(?=\[)',text) if b.startswith(('[event]','[enemy]','[npc]'))]
    destination.write_text(serialize(header,data,other))


def loop_scripts(floor,link):
    folder=ROOT/f"scripts/generation/f{floor}";folder.mkdir(parents=True,exist_ok=True)
    rects={s["procgen_link"]:tuple(map(int,s["location"].split(","))) for s in link if "procgen_link" in s}
    tiles=layers(link)
    rolls=[];candidates=[];apply=[]
    for cy in range(GRID):
        for cx in range(GRID):
            for dx,dy,a,b in ((1,0,"east","west"),(0,1,"south","north")):
                nx,ny=cx+dx,cy+dy
                if nx>=GRID or ny>=GRID:continue
                status=stable_status(f"diantre_f{floor}_loop_{cx}_{cy}_{a}")
                ax,ay=cx*SIZE+18,cy*SIZE+18
                bx,by=nx*SIZE+18,ny*SIZE+18
                px,py=(cx*SIZE+35,cy*SIZE+18) if dx else (cx*SIZE+18,cy*SIZE+35)
                for level in range(3):
                    requirement=f"topology,{ax},{ay},{LEVEL_TILE+level},topology,{bx},{by},{LEVEL_TILE+level},topology,{px},{py},0"
                    candidates.append(event(requires_tile=requirement,random_status=f"append,{status}"))
                    rolls.append(event(requires_tile=requirement,chance_exec=40,set_status=status))
                mods=[]
                for ox,oy,side in ((cx*SIZE,cy*SIZE,a),(nx*SIZE,ny*SIZE,b)):
                    x,y,w,h=rects[side]
                    for name in LAYERS:
                        for yy in range(y,y+h):
                            for xx in range(x,x+w):
                                mods.append(f"{name},{ox+xx},{oy+yy},{tiles[name][yy][xx]}")
                apply.append(event(requires_status=status,mapmod=";".join(mods)))
    selection=[event(random_status="clear"),*candidates,event(random_status="roll"),
               event(random_status="set"),event(random_status="clear"),*rolls]
    (folder/'roll.txt').write_text("\n".join(selection))
    (folder/'apply.txt').write_text("\n".join(apply))
    ready=stable_status(f"diantre_f{floor}_topology_ready")
    init=(event(requires_not_status=ready,script=f"scripts/generation/f{floor}/roll.txt")+"\n"+
          event(script=f"scripts/generation/f{floor}/apply.txt")+"\n"+
          event(requires_not_status=ready,set_status=ready,save_game="true"))
    (folder/'init.txt').write_text(init)


def main():
    metrics=[];changed=[ROOT/'settings.txt'];removed=[]
    for floor in range(1,4):
        theme=THEMES[floor];changed.append(write_palette(floor))
        source=ROOT/f"maps/iron_labyrinth/generated/f{floor}"
        dest=ROOT/f"maps/iron_labyrinth/exploration/f{floor}";dest.mkdir(parents=True,exist_ok=True)
        selected=[]
        for p in sorted(source.glob('*.txt')):
            kind=next(s for s in parse(p) if s['section']=='header')['procgen_type']
            if kind=='normal' and p.stem not in theme['landmarks']:continue
            selected.append(p.name)
            target=dest/p.name;install_copy(p,target,floor);changed.append(target)
        for family in FAMILIES:
            for variant in range(4):
                builder=Complex(floor,family,variant)
                text,data=builder.build()
                path=dest/f"complex_{family}_{variant}.txt";path.write_text(text);changed.append(path)
                selected.append(path.name)
                metrics.append({"floor":floor,"theme":theme['id'],"family":family,"variant":variant,
                                "floor_cells":len(builder.walk),"rooms":len(builder.rooms),
                                "details":len(builder.details),"inner_chapel":bool(builder.doors) and floor==3 and family in ('cloister','chambers','ring')})
        for stale in dest.glob('*.txt'):
            if stale.name not in selected:
                removed.append(stale.relative_to(ROOT).as_posix());stale.unlink()
        loop_scripts(floor,parse(dest/'links_0.txt'))
        changed.extend(sorted((ROOT/f"scripts/generation/f{floor}").glob('*.txt')))
        root=ROOT/f"maps/iron_labyrinth_f{floor}.txt"
        sections=parse(root);data=layers(sections)
        data['topology']=[[0]*len(data['collision'][0]) for _ in data['collision']]
        header=next(s for s in sections if s['section']=='header')
        header['tileset']=theme['palette'];header['title']=f"{theme['title']}: Level {floor}"
        h="[header]\n"+"\n".join(f"{k}={v}" for k,v in header.items() if k not in ('section','mapmods'))+"\n"
        raw_events=[b for b in re.split(r"\n(?=\[)",root.read_text()) if b.startswith('[event]') and 'type=diantre_exploration_init' not in b]
        raw_events.append(event(type="diantre_exploration_init",location="0,0,1,1",activate="on_load",script=f"scripts/generation/f{floor}/init.txt"))
        root.write_text(serialize(h,data,raw_events));changed.append(root)
        rules=ROOT/f"maps/procgen_rules/iron_labyrinth_f{floor}.txt"
        settings=rules.read_text().split('[chunks]')[0]
        rules.write_text(settings+'[chunks]\n'+''.join(f"filename={p.relative_to(ROOT).as_posix()}\n" for p in sorted(dest.glob('*.txt'))));changed.append(rules)
    report=Path(__file__).resolve().parents[1]/'docs/exploration-metrics.json'
    report.write_text(json.dumps({"complexes":metrics,"extra_loop_chance_percent":40,
                                 "loop_rule":"one guaranteed when eligible; same door level, normal/start/end sectors, unused exits only"},indent=2)+"\n")
    manifest_path=ROOT/'ASSET_MANIFEST.json';manifest=json.loads(manifest_path.read_text())
    for key in removed:manifest['files'].pop(key,None)
    note="Diantre 0.7.0: native ruins, caverns and crypts; themed architecture and details; original map/script data."
    for p in changed:
        key=p.relative_to(ROOT).as_posix();record=manifest['files'].get(key,{"sources":[],"changes":[]})
        raw=p.read_bytes();record.update(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
        if note not in record['changes']:record['changes'].append(note)
        manifest['files'][key]=record
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"new_complexes":len(metrics),"families":len(FAMILIES),"floors":3}))


if __name__=='__main__':
    main()
