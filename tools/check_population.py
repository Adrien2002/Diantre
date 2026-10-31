#!/usr/bin/env python3
"""Measure floor size, separated encounters and base XP budgets.

--observed uses read-only native qa_enemy records, not requested group counts.
Budgets assume all placed hostiles are defeated, without equipment/party bonuses.
They do not establish combat difficulty or a complete manual playthrough.
"""
from collections import Counter
from itertools import product
import copy
from pathlib import Path
import argparse
import json

from build_exploration import GRID, SIZE, REGION_SIZE, MAP_SIZE, PATH_RULES
from check_exploration import apply_mods
from check_surface import parse, layers, reachable
from inventory_empyrean import flatten

ROOT=Path(__file__).resolve().parents[1]/'diantre'


def level_for_xp(xp):
    levels=[tuple(map(int,line[6:].split(','))) for line in (ROOT/'engine/xp_table.txt').read_text().splitlines() if line.startswith('level=')]
    return max(level for level,threshold in levels if xp>=threshold)


def limits(group):
    nums=list(map(int,group.get('number','1').split(',')))
    return nums[0],nums[-1]


def check_assets():
    summary=[];cumulative=0
    for floor in range(1,4):
        rules=ROOT/f'maps/procgen_rules/iron_labyrinth_f{floor}.txt'
        paths=[ROOT/l.split('=',1)[1] for l in rules.read_text().splitlines() if l.startswith('filename=')]
        per_type={};normal_count=0
        link=parse(ROOT/f'maps/iron_labyrinth/exploration/f{floor}/links_0.txt');link_data=layers(link)
        strips=[tuple(map(int,s['location'].split(','))) for s in link if 'procgen_link' in s]
        for path in paths:
            sections=parse(path);h=next(s for s in sections if s['section']=='header')
            groups=[s for s in sections if s['section']=='enemy'];kind=h['procgen_type']
            per_type.setdefault(kind,[]).append(tuple(sum(limits(s)[i] for s in groups) for i in (0,1)))
            if kind!='normal':continue
            normal_count+=1
            assert 4<=len(groups)<=19,(path,'Diffuse encounter group count',len(groups))
            data=layers(sections);centres=[];counts=[]
            for g in groups:
                x,y,w,h=map(int,g['location'].split(','))
                centre=x+2,y+2;centres.append(centre)
                lo,hi=limits(g);counts.append(lo)
                assert (w,h)==(5,5) and 1<=lo==hi<=4,(path,'Variable native group',g)
                assert sum(data['collision'][yy][xx]==0
                           for yy in range(y,y+h) for xx in range(x,x+w))>=max(12,3*hi),(path,'Cramped spawn area')
            assert 11<=sum(counts)<=19,(path,'Population budget outside density band',sum(counts))
            assert 1 in counts and any(count>=3 for count in counts),(path,'Missing solitary or grouped encounters')
            assert all(abs(x1-x2)>=5 or abs(y1-y2)>=5
                       for i,(x1,y1) in enumerate(centres)
                       for x2,y2 in centres[i+1:]),(path,'Overlapping encounter regions')
            for mask,variant in product(product((False,True),repeat=4),range(3)):
                link_data=layers(parse(ROOT/f'maps/iron_labyrinth/exploration/f{floor}/links_{variant}.txt'))
                c=copy.deepcopy(data['collision'])
                for selected,(x,y,w,h) in zip(mask,strips):
                    if selected:
                        for yy in range(y,y+h):c[yy][x:x+w]=link_data['collision'][yy][x:x+w]
                for g in groups:
                    x,y,w,h=map(int,g['location'].split(','))
                    assert sum(c[yy][xx]==0 for yy in range(y,y+h) for xx in range(x,x+w))>=max(12,3*limits(g)[1]),(path,'Native edge strip removes spawn region',mask)
        assert normal_count>=GRID*GRID-4,'Unique normal pool too small for a one-gate floor'
        for kind in ('door_north_south','door_west_east','start'):
            assert all(hi==0 for lo,hi in per_type[kind])
        minimums=[];maximums=[]
        for gates in (1,2):
            normal_min=PATH_RULES['main_path_length_min']-2-2*gates
            normal_max=GRID*GRID-2-2*gates
            minimums.append(normal_min*min(p[0] for p in per_type['normal'])+
                            gates*min(p[0] for p in per_type['key'])+min(p[0] for p in per_type['end']))
            maximums.append(normal_max*max(p[1] for p in per_type['normal'])+
                            gates*max(p[1] for p in per_type['key'])+max(p[1] for p in per_type['end']))
        xp_each=2**floor;pool=[]
        for p in (ROOT/'enemies').glob('*.txt'):
            values=dict(flatten(p.relative_to(ROOT).as_posix(),[ROOT]))
            if f'diantre_depth_{floor}' not in values.get('categories','').split(','):continue
            assert int(values['xp'])==xp_each and not values.get('xp_scaling'),(p,'XP changed or adaptive')
            pool.append(p.name)
        assert pool
        low,high=min(minimums),max(maximums);cumulative+=low*xp_each
        assert level_for_xp(cumulative)>=floor+1
        summary.append(dict(floor=floor,normal_variants=normal_count,planned_hostiles_min=low,
                            planned_hostiles_max=high,xp_per_hostile=xp_each,
                            planned_base_xp_min=low*xp_each,planned_base_xp_max=high*xp_each,
                            minimum_cumulative_level=level_for_xp(cumulative)))
    return dict(grid=[GRID,GRID],region=[REGION_SIZE,REGION_SIZE],map=[MAP_SIZE,MAP_SIZE],
                area_multiplier_from_070=GRID*GRID/16,normal_group_size=[1,4],
                normal_encounter_zone=[5,5],normal_sector_population=[11,19],
                assumptions='valid native path; successful spawns; all enemies defeated; no XP bonus',floors=summary)


def check_observed(observed,cache):
    live=parse(observed);sections=parse(cache);h=next(s for s in live if s['section']=='header')
    assert int(h['width'])==int(h['height'])==MAP_SIZE
    header=next(s for s in sections if s['section']=='header')
    cells=list(map(int,header['procgen_chunks'].split(',')));assert cells[:2]==[GRID,GRID]
    assert len(cells)==2+GRID*GRID*7
    used=sum(cells[i]!=0 for i in range(2,len(cells),7))
    assert used>=PATH_RULES['main_path_length_min'],('Floor unexpectedly short',used)
    groups=[s for s in sections if s['section']=='enemy'];lo=sum(limits(s)[0] for s in groups);hi=sum(limits(s)[1] for s in groups)
    enemies=[s for s in live if s['section']=='qa_enemy'];assert enemies,'Observer did not export actual entities'
    assert lo<=len(enemies)<=hi,('Native population differs from group budget',lo,len(enemies),hi)
    assert len(enemies)>=210,('Floor is unexpectedly underpopulated',len(enemies))
    floor=next(i for i in range(1,4) if any(s.get('category')==f'diantre_depth_{i}' for s in groups))
    data=layers(live);data['collision']=[[0 if t in (7,8) else t for t in row] for row in data['collision']]
    for s in sections:
        if s['section']=='event':apply_mods(s,data)
    start=next(s for s in sections if s.get('intermap_id')=='stairs_up')
    spawn=tuple(map(int,start['location'].split(',')))[:2];seen=reachable(data['collision'],spawn)
    for enemy in enemies:
        x,y=map(float,enemy['location'].split(','))
        assert (int(x),int(y)) in seen,('Unreachable hostile',enemy)
        assert int(enemy['level'])==floor and int(enemy['xp'])==2**floor,enemy
    xp=sum(int(e['xp']) for e in enemies)
    return dict(floor=floor,occupied_sectors=used,requested_groups=len(groups),
                requested_hostiles_min=lo,requested_hostiles_max=hi,
                actual_hostiles=len(enemies),actual_base_xp=xp,
                native_enemy_types=dict(Counter(e['filename'] for e in enemies)),
                reachable_cells_after_all_local_openings=len(seen))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--observed',type=Path);p.add_argument('--cache',type=Path)
    a=p.parse_args()
    if a.observed:assert a.cache;result=check_observed(a.observed,a.cache)
    else:result=check_assets()
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
