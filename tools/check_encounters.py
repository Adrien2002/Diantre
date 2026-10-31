#!/usr/bin/env python3
"""Reject player-dependent spawn levels in all active dungeon encounter pools."""
from pathlib import Path
import json

from check_surface import parse
from inventory_empyrean import flatten

ROOT=Path(__file__).resolve().parents[1]/'diantre'


def main():
    files=sorted((ROOT/'enemies').glob('*.txt'));pools={};groups=0;chunks=0
    floors=sorted((ROOT/'maps').glob('iron_labyrinth_f*.txt'))
    assert floors,'No active dungeon floors'
    for base in floors:
        floor=int(base.stem.rsplit('f',1)[1])
        category=f'diantre_depth_{floor}';members=[]
        for path in files:
            rows=flatten(path.relative_to(ROOT).as_posix(),[ROOT]);values=dict(rows)
            if category not in values.get('categories','').split(','):
                continue
            assert int(values['level'])>0,(path,'Missing native enemy level')
            assert not any(k=='stat_per_level' for k,v in rows),(path,'Adaptive enemy in a fixed pool')
            assert not path.name.startswith('il_'),(path,'Labyrinth enemy in a campaign pool')
            members.append({'file':path.name,'native_level':int(values['level'])})
        assert members,('Empty floor pool',floor)
        pools[str(floor)]=members
        rules=ROOT/f'maps/procgen_rules/iron_labyrinth_f{floor}.txt'
        paths=[ROOT/line.split('=',1)[1] for line in rules.read_text().splitlines() if line.startswith('filename=')]
        chunks+=len(paths)
        for path in [base,*paths]:
            for s in parse(path):
                if s['section']!='enemy':
                    continue
                assert s.get('spawn_level','default')=='default',(path,'Player-dependent or overridden spawn level')
                assert s.get('category')==category,(path,'Wrong depth pool')
                groups+=1
    print(json.dumps({'active_floors':len(floors),'modules':chunks,'enemy_groups':groups,'fixed_pools':pools},indent=2))


if __name__=='__main__':
    main()
