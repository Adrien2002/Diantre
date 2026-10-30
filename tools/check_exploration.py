#!/usr/bin/env python3
"""Verify complexes, runtime loop rules, and observed engine floors.

Use --observed EXPORT --cache NATIVE_CACHE --avatar AVATAR to inspect a real
engine state. EXPORT is a read-only dump of live layers and collider; the
unmodified procedural cache supplies the original events and exits.
"""
from pathlib import Path
from itertools import product
import argparse
import copy
import hashlib
import json
import re

from check_surface import parse, layers, reachable

ROOT=Path(__file__).resolve().parents[1]/'diantre'
PORTS=((18,0),(18,35),(0,18),(35,18))


def gnu_status_hash(text,bits):
    value=0;mask=(1<<bits)-1
    for b in text.encode():
        value=(((value<<7)&mask)|(value>>(bits-7)))+b
        value&=mask
    return value


def check_status_hashes():
    from build_exploration import stable_status
    a,b='diantre_f1_loop_1_1_south','diantre_f3_loop_1_0_south'
    assert gnu_status_hash(a,64)==gnu_status_hash(b,64)
    assert gnu_status_hash(stable_status(a),64)!=gnu_status_hash(stable_status(b),64)
    statuses=set()
    for path in ROOT.rglob('*.txt'):
        for line in path.read_text(errors='replace').splitlines():
            if re.match(r'^(set_status|requires_status|requires_not_status|unset_status|procgen_unique_status)=',line):
                statuses.update(s for s in line.split('=',1)[1].split(',') if s and not s.startswith('('))
    for bits in (32,64):
        seen={}
        for s in sorted(statuses):
            h=gnu_status_hash(s,bits)
            assert h!=0 and (h not in seen or seen[h]==s),('Status hash collision',bits,s,seen.get(h))
            seen[h]=s
    return len(statuses)


def apply_mods(section,data):
    for mod in section['mapmods']:
        layer,x,y,tile=mod.split(',')
        data[layer][int(y)][int(x)]=int(tile)


def neighbours(section,seen):
    x,y,w,h=map(int,section['location'].split(','))
    return any((xx+dx,yy+dy) in seen for yy in range(y,y+h) for xx in range(x,x+w)
               for dx,dy in ((0,0),(1,0),(-1,0),(0,1),(0,-1)))


def check_assets():
    combinations=0;geometries=set();puzzles=0;families=set()
    for floor in range(1,4):
        folder=ROOT/f'maps/iron_labyrinth/exploration/f{floor}'
        link=parse(folder/'links_0.txt');ld=layers(link)
        rects=[tuple(map(int,s['location'].split(','))) for s in link if 'procgen_link' in s]
        for p in folder.glob('*.txt'):
            ss=parse(p);h=next(s for s in ss if s['section']=='header');data=layers(ss)
            assert h['width']==h['height']=='36'
            assert list(data)==['background','background_fringe','object','topology','collision']
            assert all(len(v)==36 and all(len(row)==36 for row in v) for v in data.values())
            markers=[s for s in ss if any(m.startswith('topology,18,18,409') for m in s['mapmods'])]
            assert len(markers)==(3 if h['procgen_type'] in ('normal','start','end') else 0),(p,'incorrect stage advertising')
            if not p.name.startswith('complex_'):continue
            families.add(p.stem.rsplit('_',1)[0])
            geometries.add(tuple(tuple(row) for row in data['collision']))
            assert all(data['collision'][0][i] and data['collision'][35][i]
                       and data['collision'][i][0] and data['collision'][i][35] for i in range(36))
            for mask,link_variant in product(product((False,True),repeat=4),range(3)):
                if not any(mask):continue
                ld=layers(parse(folder/f'links_{link_variant}.txt'))
                d=copy.deepcopy(data)
                for on,(x,y,w,h) in zip(mask,rects):
                    if on:
                        for name in d:
                            for yy in range(y,y+h):d[name][yy][x:x+w]=ld[name][yy][x:x+w]
                for s in ss:apply_mods(s,d)
                ports=[p for on,p in zip(mask,PORTS) if on]
                seen=reachable(d['collision'],ports[0])
                assert all(p in seen for p in ports),(p,'disconnected selected exit')
                assert all(neighbours(s,seen) for s in ss if s.get('tooltip') in ('Treasure Chest','Vault Seal','Door')),(p,'unreachable interaction')
                combinations+=1
            if '_vault_' in p.name:
                puzzles+=1
                d=copy.deepcopy(data)
                for x,y,w,h in rects:
                    for name in d:
                        for yy in range(y,y+h):d[name][yy][x:x+w]=ld[name][yy][x:x+w]
                chest=next(s for s in ss if s.get('tooltip')=='Treasure Chest')
                initial=reachable(d['collision'],PORTS[0])
                assert not neighbours(chest,initial),'Vault reachable before its seals'
                seals=[s for s in ss if s.get('tooltip')=='Vault Seal']
                assert len(seals)==2 and all(neighbours(s,initial) for s in seals)
                opening=next(s for s in ss if s.get('activate')=='static')
                required=set(opening['requires_status'].split(','))
                assert required=={s['set_status'] for s in seals},'Both distinct seals must be required'
                for seal in seals:
                    one=copy.deepcopy(d);apply_mods(seal,one)
                    assert not neighbours(chest,reachable(one['collision'],PORTS[0]))
                apply_mods(opening,d)
                assert neighbours(chest,reachable(d['collision'],PORTS[0]))
                assert all(d['background'][y][25] for y in (28,29)),'No floor under opened gate'
        roll=parse(ROOT/f'scripts/generation/f{floor}/roll.txt')
        apply=parse(ROOT/f'scripts/generation/f{floor}/apply.txt')
        assert len(roll)==148 and len(apply)==24
        assert roll[0].get('random_status')=='clear'
        assert [s.get('random_status') for s in roll[73:76]]==['roll','set','clear']
        assert all(s.get('random_status','').startswith('append,') for s in roll[1:73])
        for s in roll:
            if 'requires_tile' not in s:continue
            req=s['requires_tile'].split(',')
            assert len(req)==12
            assert req[0]==req[4]==req[8]=='topology'
            assert req[3]==req[7] and req[3] in ('4096','4097','4098')
            assert req[11]=='0','Only an unused exit can be opened'
            ax,ay,bx,by=map(int,(req[1],req[2],req[5],req[6]))
            assert abs(ax-bx)+abs(ay-by)==36
        for s in apply:
            sectors=set()
            for mod in s['mapmods']:
                name,x,y,tile=mod.split(',');x,y,tile=int(x),int(y),int(tile)
                assert 0<=x<144 and 0<=y<144
                sectors.add((x//36,y//36))
                if name=='topology':assert tile in (0,4100)
                assert not (25<=x%36<=33 and 25<=y%36<=33)
            assert len(sectors)==2,'Both ends must open atomically'
    return {'complex_configurations':combinations,'families':len(families),'status_names_checked':check_status_hashes(),
            'distinct_complex_collisions':len(geometries),'two_seal_puzzles':puzzles,
            'stage_safe_candidate_edges':72}


def check_observed(observed,cache,avatar):
    data=layers(parse(observed));ss=parse(cache)
    # Native values 7/8 are transient actor occupants of walkable terrain.
    data['collision']=[[0 if t in (7,8) else t for t in row] for row in data['collision']]
    text=avatar.read_text();campaign=next(l.split('=',1)[1] for l in text.splitlines() if l.startswith('campaign='))
    status=set(campaign.split(','))
    floor=next(i for i in range(1,4) if f'emp_il_f{i}' in status)
    assert any(s.endswith(f'_diantre_f{floor}_topology_ready') for s in status),'Runtime initialization did not finish'
    c=data['collision'];initial=copy.deepcopy(c)
    selected=[s for s in parse(ROOT/f'scripts/generation/f{floor}/apply.txt') if s['requires_status'] in status]
    eligible_left=0
    for s in parse(ROOT/f'scripts/generation/f{floor}/roll.txt'):
        if 'chance_exec' not in s:continue
        req=s['requires_tile'].split(',')
        if all(data['topology'][int(req[i+2])][int(req[i+1])]==int(req[i+3]) for i in range(0,12,4)):
            eligible_left+=1
    assert selected or not eligible_left,'A safe loop was available but none was selected'
    for s in selected:
        pieces=s['requires_status'].split('_');cx,cy=int(pieces[-3]),int(pieces[-2]);side=pieces[-1]
        nx,ny=cx+(side=='east'),cy+(side=='south')
        a,b=data['topology'][cy*36+18][cx*36+18],data['topology'][ny*36+18][nx*36+18]
        assert a==b and a in (4096,4097,4098),'Loop crosses a progression gate'
        for mod in s['mapmods']:
            layer,x,y,tile=mod.split(',');x,y,tile=int(x),int(y),int(tile)
            assert data[layer][y][x]==tile,(observed,'Runtime loop differs from its script',layer,x,y)
    start=next(s for s in ss if s.get('intermap_id')=='stairs_up')
    spawn=tuple(map(int,start['location'].split(',')))[:2]
    goal=next(s for s in ss if s.get('tooltip') in ('Stairs Down','Return to Town'))
    events=[s for s in ss if s['section']=='event'];done=set();keys=0;gates=[]
    while True:
        seen=reachable(c,spawn);changed=False
        for s in events:
            label=s.get('tooltip');token=(label,s.get('location'))
            if token in done or not neighbours(s,seen):continue
            if label=='Key Chest':
                keys+=1;done.add(token);changed=True
            elif label in ('Door','Vault Lever') or (label=='Locked Door' and 'requires_item' in s and keys>0):
                if label=='Locked Door':keys-=1;gates.append(s)
                apply_mods(s,data);done.add(token);changed=True
        if not changed:break
    assert neighbours(goal,seen),'Native progression cannot reach the end'
    for gate in gates:
        closed=copy.deepcopy(c)
        for mod in gate['mapmods']:
            layer,x,y,tile=mod.split(',')
            if layer=='collision':closed[int(y)][int(x)]=1
        assert not neighbours(goal,reachable(closed,spawn)),'Mandatory gate can be bypassed'
    geometry_hash=hashlib.sha256(bytes(t for row in initial for t in row)).hexdigest()
    return {'floor':floor,'runtime_loops':len(selected),'mandatory_gates':len(gates),
            'complex_families':sorted(s for s in status if f'diantre_f{floor}_complex_' in s),
            'collision_sha256':geometry_hash,'reachable_after_keys':len(seen)}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--observed',type=Path);parser.add_argument('--cache',type=Path);parser.add_argument('--avatar',type=Path)
    a=parser.parse_args()
    if a.observed:
        assert a.cache and a.avatar
        result=check_observed(a.observed,a.cache,a.avatar)
    else:result=check_assets()
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
