#!/usr/bin/env python3
"""Extract Empyrean's fixed enemy variants and possible campaign map placements.

Usage: python3 tools/inventory_empyrean.py --game ../flare-game
The supplied checkout supplies the data; no download is performed by this tool.
Placements are category/level matches, not a chronological campaign walkthrough.
"""
from pathlib import Path
import argparse
import csv
import io
import json
import re
import subprocess


def flatten(relative, roots, stack=()):
    if relative in stack:
        raise ValueError(f"Cyclic INCLUDE: {relative}")
    path=next((root/relative for root in roots if (root/relative).is_file()),None)
    if path is None:
        raise FileNotFoundError(relative)
    rows=[]
    for raw in path.read_text().splitlines():
        line=raw.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('INCLUDE '):
            rows.extend(flatten(line[8:].strip(),roots,stack+(relative,)))
        elif '=' in line:
            rows.append(tuple(line.split('=',1)))
    return rows


def map_groups(path):
    title=path.stem;section='';rows=[];blocks=[]
    for raw in path.read_text().splitlines()+['[end]']:
        line=raw.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('['):
            blocks.append((section,rows));section=line[1:-1];rows=[]
        elif '=' in line:
            rows.append(tuple(line.split('=',1)))
    for section,rows in blocks:
        values=dict(rows)
        if section=='header':
            title=values.get('title',title)
    for section,rows in blocks:
        values=dict(rows)
        if section=='enemy' and 'category' in values:
            limits=[int(x) for x in values.get('level','0').split(',')]
            low=limits[0];high=max(low,limits[-1])
            yield values['category'],low,high,title,'group',values.get('spawn_level','default')
        elif section=='event':
            for key,value in rows:
                if key=='spawn':
                    yield value.split(',')[0],0,0,title,'event','event-defined'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'docs/bestiary')
    args=parser.parse_args();game=args.game.resolve()
    roots=[game/'mods/empyrean_campaign',game/'mods/fantasycore',game/'mods/minicore']
    revision=subprocess.check_output(['git','-C',str(game),'rev-parse','HEAD'],text=True).strip()
    placements=[]
    for path in sorted((roots[0]/'maps').rglob('*.txt')):
        if path.stem.startswith('iron_labyrinth') or 'iron_labyrinth' in path.parts:
            continue
        for cat,low,high,title,kind,mode in map_groups(path):
            placements.append((cat,low,high,title,path.relative_to(game).as_posix(),kind,mode))
    enemies=[]
    for path in sorted((roots[0]/'enemies').glob('lvl*.txt')):
        virtual=path.relative_to(roots[0]).as_posix();rows=flatten(virtual,roots);values=dict(rows)
        if 'level' not in values or 'name' not in values:
            continue
        stats={v.split(',')[0]:v.split(',')[1] for k,v in rows if k=='stat' and ',' in v}
        level=int(values['level']);categories=values.get('categories','').split(',')
        maps=[]
        for cat,low,high,title,filename,kind,mode in placements:
            if cat in categories and (low==high==0 or low<=level<=high):
                maps.append({'file':filename,'title':title,'kind':kind,'spawn_level':mode})
        maps=list({(m['file'],m['kind'],m['spawn_level']):m for m in maps}.values())
        enemies.append({'file':path.relative_to(game).as_posix(),'name':values['name'],
            'level':level,'rarity':values.get('rarity','common'),'hp':int(stats.get('hp',0)),
            'categories':categories,'stats':stats,
            'powers':[v for k,v in rows if k=='power'],
            'passive_powers':values.get('passive_powers',''),
            'defeat_status':values.get('defeat_status',''),
            'wrapper':bool(re.match(r'lvl\d+_spawn_',path.stem)),
            'possible_campaign_maps':maps})
    enemies.sort(key=lambda e:(e['level'],e['name'],e['file']))
    assert enemies and all(e['level']>0 and e['hp']>0 for e in enemies)
    by_name={e['name']:e for e in enemies}
    for name,level in [('Seagate',4),('Mez',8),('Metzger',12),('Lezaith',16)]:
        assert by_name[name]['level']==level and by_name[name]['possible_campaign_maps'],name
    args.output.mkdir(parents=True,exist_ok=True)
    payload={'source_repository':'https://github.com/flareteam/flare-game',
        'source_revision':revision,
        'scope':'Empyrean lvl* variants, including inherited fields and spawn wrappers; excludes adaptive il_* enemies and player summons',
        'map_matching':'Possible category/level matches and event spawns outside Iron Labyrinth; not chronology or guaranteed appearances',
        'enemies':enemies}
    (args.output/'empyrean-enemies.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    buffer=io.StringIO();writer=csv.writer(buffer,lineterminator='\n')
    writer.writerow(['name','native_level','hp','rarity','categories','defeat_status','spawn_wrapper','possible_campaign_maps','source_file'])
    for e in enemies:
        writer.writerow([e['name'],e['level'],e['hp'],e['rarity'],','.join(e['categories']),e['defeat_status'],e['wrapper'],
                         '; '.join(sorted({m['title'] for m in e['possible_campaign_maps']})),e['file']])
    (args.output/'empyrean-enemies.csv').write_text(buffer.getvalue())
    lines=['# Bestiaire de référence d’Empyrean','',
        f"Source : [flareteam/flare-game, {revision[:12]}](https://github.com/flareteam/flare-game/tree/{revision}).",'',
        'Les niveaux et les points de vie proviennent des définitions natives, INCLUDE résolus.',
        'Chaque ligne est une variante de données, pas nécessairement une espèce distincte.',
        'Les cartes sont des correspondances possibles par catégorie et niveau ou par événement ;',
        'elles ne constituent pas un ordre chronologique garanti. Les variantes `spawn` sont signalées.',
        'Les ennemis adaptatifs `il_*` du Labyrinthe de fer et les invocations du joueur sont exclus.','',
        '| Niveau natif | Ennemi | PV | Repère de campagne |',
        '| --- | --- | ---: | --- |']
    for e in enemies:
        location=' ; '.join(sorted({m['title'] for m in e['possible_campaign_maps']})) or 'Non trouvé dans les groupes/événements analysés'
        source=f"https://github.com/flareteam/flare-game/blob/{revision}/{e['file']}"
        name=e['name']+(' (variante de groupe)' if e['wrapper'] else '')
        lines.append(f"| {e['level']} | [{name}]({source}) | {e['hp']} | {location.replace('|','/')} |")
    (args.output/'LISEZ-MOI.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'variants':len(enemies),'native_levels':sorted({e['level'] for e in enemies}),
                      'with_map_reference':sum(bool(e['possible_campaign_maps']) for e in enemies),
                      'source_revision':revision}))


if __name__=='__main__':
    main()
