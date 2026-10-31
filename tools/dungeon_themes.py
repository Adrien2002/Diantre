#!/usr/bin/env python3
"""Native atlas selections for the three dungeon environments.

Tile numbers are a shared logical vocabulary. Atlas images are never edited.
Interactive objects keep their 0.6 IDs so map events and saved states agree.
"""
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]/'diantre'
THEMES={
    1:dict(id='ruins',title='Ancient Ruins',palette='tilesetdefs/diantre_dungeon.txt',
           landmarks={'great_hall_0','basilica_0','courtyard_0','cavern_0'},props=(512,513)),
    2:dict(id='caverns',title='Buried Caverns',palette='tilesetdefs/diantre_caverns.txt',
           landmarks={'cavern_0'},props=(512,513,514)),
    3:dict(id='crypts',title='Stone Crypts',palette='tilesetdefs/diantre_crypts.txt',
           landmarks={'great_hall_0','basilica_0'},props=(512,513,514,515)),
}


def read_palette(relative):
    tiles={};animations={};image=None
    for raw in (ROOT/relative).read_text().splitlines():
        line=raw.strip()
        if line.startswith('INCLUDE '):
            other,anim=read_palette(line[8:]);tiles.update(other);animations.update(anim)
        elif line.startswith('img='):
            image=line[4:]
        elif line.startswith('tile='):
            tile,*coords=map(int,line[5:].split(','));tiles[tile]=(image,coords)
        elif line.startswith('animation='):
            tile=int(line.split('=',1)[1].split(';',1)[0]);animations[tile]=line
    return tiles,animations


def write_palette(floor):
    theme=THEMES[floor];tiles,animations=read_palette('tilesetdefs/tileset_ruins.txt')
    sources={name:read_palette(f'tilesetdefs/tileset_{name}.txt') for name in ('ruins','cave','dungeon')}
    def alias(target,atlas,native,raise_by=0):
        definitions,anims=sources[atlas];image,coords=definitions[native];coords=coords.copy();coords[-1]+=raise_by
        tiles[target]=(image,coords);animations.pop(target,None)
        if native in anims and raise_by==0:
            animations[target]='animation='+str(target)+';'+anims[native].split(';',1)[1]
    if floor==2:
        for tile in range(24,120):alias(tile,'cave',16+(tile-24)%16)
        # These standalone boulders have complete textured faces. The native
        # tall cave-wall pieces contain black backs and are deliberately unused.
        for tile in range(136,152):alias(tile,'cave',153)
        alias(152,'cave',147)
        for tile in range(153,161):alias(tile,'cave',16+(tile-153)%8,190)
        for target,native in [(512,147),(513,150),(514,153),(515,151),
                              (530,32),(531,33),(532,48),(533,49),(534,50),(535,51),(536,52),(537,53)]:
            alias(target,'cave',native)
    elif floor==3:
        floors=(16,17,18,19,36,37,44,47)
        for tile in range(24,120):alias(tile,'dungeon',floors[(tile-24)%len(floors)])
        # Reuse the complete masonry blocks for structural walls; dungeon
        # niches have black reverse faces and are unsuitable as isolated walls.
        for tile in range(153,161):alias(tile,'dungeon',floors[tile-153],190)
        alias(152,'dungeon',118)
        for target,native in [(512,128),(513,136),(514,194),(515,167),
                              (530,32),(531,33),(532,34),(533,35),(534,176),(535,177),(536,178),(537,179)]:
            alias(target,'dungeon',native)
    else:
        alias(512,'ruins',152);alias(513,'cave',151);alias(514,'dungeon',176);alias(515,'dungeon',167)
        for target in range(530,538):alias(target,'ruins',24+(target-530)%8)
    for marker in (4096,4097,4098,4100):
        tiles[marker]=('images/tilesets/tileset_ruins.png',[0,0,1,1,0,0])
    groups=defaultdict(list)
    for tile,(image,coords) in sorted(tiles.items()):groups[image].append((tile,coords))
    parts=[f'# Diantre 0.8.0: {theme["id"]}; native atlas images unchanged.']
    for image,entries in groups.items():
        parts.extend(['','[tileset]',f'img={image}'])
        for tile,coords in entries:
            parts.append('tile='+','.join(map(str,[tile,*coords])))
            if tile in animations:parts.append(animations[tile])
    path=ROOT/theme['palette'];path.write_text('\n'.join(parts)+'\n');return path


def dress_layers(floor,data):
    """Give the legacy special rooms and links the same ground as new rooms."""
    for y,row in enumerate(data['background']):
        for x,tile in enumerate(row):
            if tile==0:row[x]=24+(x*3+y*5)%8


def add_details(builder,data):
    """Place a few obstacles in spacious pockets, clear of ports and rewards."""
    protected=[*builder.props,*builder.rooms[:1],*(p for points in builder.doors for p in points)]
    protected.extend(((18,7),(18,28),(7,18),(28,18)))
    candidates=[]
    for x,y in sorted(builder.walk):
        if (x,y) in builder.reserved or any(abs(x-px)+abs(y-py)<5 for px,py in protected):continue
        if all((x+dx,y+dy) in builder.walk for dx in range(-2,3) for dy in range(-2,3)):
            candidates.append((x,y))
    builder.rng.shuffle(candidates);placed=[];theme=THEMES[builder.floor]
    # Keep large passageways clear, but give substantial open rooms more
    # environmental landmarks than the old four-object hard limit.
    target=min(11,max(6,len(candidates)//35))
    for x,y in candidates:
        if len(placed)>=target:break
        if any(abs(x-px)+abs(y-py)<5 for px,py in placed):continue
        tile=theme['props'][len(placed)%len(theme['props'])]
        data['object'][y][x]=tile;data['collision'][y][x]=2;placed.append((x,y))
    if builder.floor==2 and builder.family in ('gallery','barracks'):
        # Straight mining traces belong on straight excavations, not random
        # disconnected rail turns. Never alter the movement layer.
        for x in range(5,31):
            if all((x+dx,18+dy) in builder.walk for dx in (-1,0,1) for dy in (-1,0,1)):
                if data['object'][18][x]==0:data['background_fringe'][18][x]=530
    elif builder.floor==3:
        for y in range(4,32):
            if data['collision'][y][18]==0 and data['object'][y][18]==0:
                data['background_fringe'][y][18]=530+(y%4)
    return placed
