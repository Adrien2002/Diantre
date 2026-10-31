#!/usr/bin/env python3
"""Check active native palettes, wall backs, themed rooms and floor difficulty."""
from pathlib import Path
import hashlib
import json

from PIL import Image
from check_surface import parse,layers,reachable
from dungeon_themes import ROOT,THEMES,read_palette
from check_exploration import apply_mods,neighbours
from build_exploration import MAP_SIZE, REGION_SIZE


def main():
    images={};summary=[];all_shapes=[]
    for floor,theme in THEMES.items():
        tiles,animations=read_palette(theme['palette']);checked=0;chapels=0;details=0;rails=0;shapes=set()
        for tile,(image,coords) in tiles.items():
            if image not in images:images[image]=Image.open(ROOT/image).convert('RGBA')
            atlas=images[image];x,y,w,h,ox,oy=coords
            assert 0<=x<x+w<=atlas.width and 0<=y<y+h<=atlas.height,(floor,tile,'invalid atlas rectangle')
        for tile in (*range(136,152),*range(153,161)):
            image,(x,y,w,h,*_) = tiles[tile]
            sample=images[image].crop((x,y,x+w,y+h))
            pixels=sample.get_flattened_data() if hasattr(sample,'get_flattened_data') else sample.getdata()
            assert not any(a>240 and max(r,g,b)<3 for r,g,b,a in pixels),(floor,tile,'opaque black wall back')
        for marker in (4096,4097,4098,4100):
            image,(x,y,w,h,*_)=tiles[marker]
            assert images[image].getpixel((x,y))[3]==0,'Visible topology marker'
        root=ROOT/f'maps/iron_labyrinth_f{floor}.txt'
        header=next(s for s in parse(root) if s['section']=='header')
        assert header['tileset']==theme['palette'] and header['title']==f"{theme['title']}: Level {floor}"
        assert int(header['width'])==int(header['height'])==MAP_SIZE
        region=next(s for s in parse(root) if 'procgen_filename' in s)
        assert region['location']==f'0,0,{REGION_SIZE},{REGION_SIZE}'
        folder=ROOT/f'maps/iron_labyrinth/exploration/f{floor}'
        for path in sorted(folder.glob('*.txt')):
            ss=parse(path);header=next(s for s in ss if s['section']=='header');data=layers(ss)
            assert header['tileset']==theme['palette']
            for name,rows in data.items():
                if name=='collision':continue
                assert {t for row in rows for t in row}<={0,*tiles},(path,name,'undefined tile')
            assert all(t for row in data['background'] for t in row),'Missing ground beneath structure'
            if not path.name.startswith('complex_'):continue
            checked+=1;details+=sum(512<=t<=515 for row in data['object'] for t in row)
            rails+=sum(t in (530,531) for row in data['background_fringe'] for t in row)
            shapes.add(hashlib.sha256(bytes(t for row in data['collision'] for t in row)).hexdigest())
            for door in (s for s in ss if s.get('tooltip')=='Door'):
                x,y,w,h=map(int,door['location'].split(','))
                assert (w,h)==(2,1) and data['object'][y][x:x+2]==[378,379],(path,'misaligned horizontal door')
            for gate in (s for s in ss if s.get('activate')=='static' and '_complex_vault_' in s.get('set_status','')):
                x,y,w,h=map(int,gate['location'].split(','))
                assert (w,h)==(1,2) and [data['object'][y+i][x] for i in range(2)]==[377,376],(path,'misaligned vertical gate')
            family=path.stem.rsplit('_',1)[0].removeprefix('complex_')
            if floor==3 and family in ('cloister','chambers','ring'):
                chapels+=1
                chest=next(s for s in ss if s.get('tooltip')=='Treasure Chest')
                door=next(s for s in ss if s.get('tooltip')=='Door')
                c=data['collision'];before=reachable(c,(18,7))
                assert neighbours(door,before) and not neighbours(chest,before),(path,'inner chapel is not enclosed')
                apply_mods(door,data)
                assert neighbours(chest,reachable(c,(18,7))),(path,'inner chapel door does not grant access')
        assert checked==32 and details>0
        if floor==2:assert rails>0
        if floor==3:assert chapels==12
        summary.append({'floor':floor,'theme':theme['id'],'palette':theme['palette'],'complexes':checked,
                        'distinct_shapes':len(shapes),'decorative_obstacles':details,'rail_or_nave_cells':rails,'inner_chapels':chapels})
        all_shapes.append(shapes)
    assert all_shapes[0]!=all_shapes[1] and all_shapes[1]!=all_shapes[2],'Themes only change colors'
    manifest=json.loads((ROOT/'ASSET_MANIFEST.json').read_text())
    for relative,record in manifest['files'].items():
        path=ROOT/relative
        assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==record['sha256'],relative
    print(json.dumps({'themes':summary,'asset_hashes_checked':len(manifest['files']),
                      'opaque_black_structural_faces':0},indent=2))


if __name__=='__main__':main()
