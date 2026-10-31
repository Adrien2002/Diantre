#!/usr/bin/env python3
"""Headless native QA for the three environments, using disposable test saves.

Requires a lab with build/flare (qa-flare-export.patch applied) and extracted
Xvfb/xdotool dependencies under sysroot/usr. Example:
  python3 tools/qa_themes_native.py --lab ../diantre-theme-lab --engine-repo ../flare-engine
No player save/config directory is read or modified. Flare must be stopped
before rebuilding the executable. Run this process without other concurrent
commands writing the lab filesystem.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import time

from check_surface import parse,layers,reachable
from check_exploration import check_observed,neighbours
from dungeon_themes import THEMES

ROOT=Path(__file__).resolve().parents[1]
MAP_HASH={1:'7811557995279168839',2:'7811557995547604295',3:'7811557995816039751'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lab',type=Path,required=True)
    parser.add_argument('--engine-repo',type=Path,required=True)
    args=parser.parse_args();lab=args.lab.resolve();engine=args.engine_repo.resolve()
    stamp=str(time.time_ns());out=lab/('native-'+stamp);out.mkdir()
    cfg=out/'config/flare';cfg.mkdir(parents=True)
    game=lab/'game/mods';game.mkdir(parents=True,exist_ok=True)
    for name,target in [('default',engine/'mods/default'),('diantre',ROOT/'diantre')]:
        if not (game/name).exists():(game/name).symlink_to(target)
    if not Path('/usr/bin/xkbcomp').exists():Path('/usr/bin/xkbcomp').symlink_to(lab/'sysroot/usr/bin/xkbcomp')
    env=os.environ.copy();env.update(DISPLAY='127.0.0.1:98',LD_LIBRARY_PATH=str(lab/'sysroot/usr/lib/x86_64-linux-gnu'),XDG_CONFIG_HOME=str(out/'config'))
    logs=[];process=None;save=None
    def logfile(name):
        f=(out/name).open('w');logs.append(f);return f
    xvfb=subprocess.Popen([str(lab/'sysroot/usr/bin/Xvfb'),':98','-screen','0','1280x720x24','-nolisten','local','-nolisten','unix','-listen','tcp','-ac'],env=env,stdout=logfile('xvfb.log'),stderr=subprocess.STDOUT)
    def settings(overview=False):
        h=4800 if overview else 960
        (cfg/'settings.txt').write_text(f'fullscreen=0\nresolution_w=1280\nresolution_h=720\nmin_render_size={h}\nmax_render_size={h}\nrenderer=sdl\nmouse_move=1\ndev_mode=1\ndev_hud=0\nminimap_mode=2\nlanguage=en\nsetup_language=1\nsetup_mousemove=1\npause_on_focus_loss=0\n')
    def data_root(label):
        nonlocal save
        path=out/('userdata-'+label);path.mkdir()
        env['XDG_DATA_HOME']=str(path);save=path/'flare/saves/diantre/1'
    def halt():
        if process and process.poll() is None:process.terminate();process.wait(timeout=10)
    def start(label,load=True,overview=False):
        nonlocal process
        settings(overview)
        cmd=[str(lab/'build/flare'),'--data-path='+str(lab/'game'),'--mods=diantre','--renderer=sdl','--no-audio']
        if load:cmd.append('--load-slot=1')
        process=subprocess.Popen(cmd,env=env,cwd=out,stdout=logfile(label+'.log'),stderr=subprocess.STDOUT)
        time.sleep(7 if not load else 4)
        assert process.poll() is None,('Flare exited',label)
    def inp(*a):subprocess.run([str(lab/'sysroot/usr/bin/xdotool'),*map(str,a)],env=env,check=True,timeout=20)
    def click(x,y):inp('mousemove',x,y,'mousedown',1);time.sleep(.15);inp('mouseup',1)
    def console(text):
        inp('key','--delay',180,'F5');time.sleep(.15);inp('type','--delay',45,text)
        inp('key','--delay',180,'Return');time.sleep(.15);inp('key','--delay',180,'F5')
        inp('keyup','Shift_L','Shift_R','Control_L','Control_R');time.sleep(.7)
    def dump(name):
        console('qa_dump '+name);path=out/name;assert path.exists(),path;return path
    def record(name):
        dest=out/name;dest.mkdir()
        for p in (save/'maps').glob('*.txt'):shutil.copyfile(p,dest/p.name)
        shutil.copyfile(save/'avatar.txt',dest/'avatar.txt');return dest
    def screenshot(name):
        inp('mousemove',1275,715)
        subprocess.run(['import','-display',env['DISPLAY'],'-window','root',str(out/name)],env=env,check=True,timeout=30)
    def terrain(path):
        d=layers(parse(path));d['collision']=[[0 if t in (7,8) else t for t in row] for row in d['collision']];return d
    def flags():return set(next(l[9:] for l in (save/'avatar.txt').read_text().splitlines() if l.startswith('campaign=')).split(','))
    def restore_fixture(state,label):
        halt();data_root(label);(save/'maps').mkdir(parents=True)
        shutil.copyfile(state/'avatar.txt',save/'avatar.txt');(save/'stash_HC.txt').write_text('')
        for p in state.glob('*.txt'):
            if p.name!='avatar.txt':shutil.copyfile(p,save/'maps'/p.name)
        start(label)
    def press(target,data):
        x,y,w,h=map(int,target['location'].split(','));tx,ty=x+w//2,y+h//2
        candidates=[(xx,yy) for yy in range(max(0,y-2),y+h+2) for xx in range(max(0,x-2),x+w+2)
                    if data['collision'][yy][xx]==0 and not (x<=xx<x+w and y<=yy<y+h)]
        sx,sy=min(candidates,key=lambda p:abs(p[0]-tx)+abs(p[1]-ty))
        console(f'/intramap={sx},{sy} restore=hpmp');dx,dy=tx-sx,ty-sy
        click(640+(dx-dy)*72,360+(dx+dy)*36);time.sleep(.6);return sx,sy
    records=[];chapel_fixture=None;vault_fixture=None;report={}
    try:
        time.sleep(1);data_root('initial');start('initial',load=False)
        screenshot('initial-title.png')
        click(830,498);time.sleep(3);screenshot('initial-character.png')
        click(760,168);time.sleep(.5);click(354,691);time.sleep(4)
        screenshot('initial-created.png')
        assert (save/'avatar.txt').exists(),'Native character creation failed'
        template=(save/'avatar.txt').read_text();(out/'native-avatar-template.txt').write_text(template);halt()
        for run in range(1,4):
            data_root(f'run{run}');save.mkdir(parents=True)
            text=re.sub(r'^spawn=.*$','spawn=maps/iron_labyrinth_f1.txt,0,0',template,flags=re.M)
            text=re.sub(r'^campaign=.*$','campaign=diantre_town_hamlet_forest',text,flags=re.M)
            (save/'avatar.txt').write_text(text);(save/'stash_HC.txt').write_text('')
            assert not (save/'maps').exists(),'The generation series is not fresh'
            start(f'run{run}')
            for floor in range(1,4):
                if floor>1:console(f'/intermap=maps/iron_labyrinth_f{floor}.txt,-1,-1,stairs_up')
                observed=dump(f'run{run}-f{floor}.txt');state=record(f'run{run}-f{floor}-state')
                cache=state/(MAP_HASH[floor]+'.txt');ss=parse(cache)
                assert next(s for s in ss if s['section']=='header')['tileset']==THEMES[floor]['palette']
                result=check_observed(observed,cache,state/'avatar.txt');result['run']=run;records.append(result)
                (out/'native-results.json').write_text(json.dumps(records,indent=2)+'\n')
                print(json.dumps({'run':run,'floor':floor,'loops':result['runtime_loops'],'gates':result['mandatory_gates']}),flush=True)
                if floor==3 and chapel_fixture is None:
                    doors=[s for s in ss if s.get('tooltip')=='Door' and any('_complex_'+f+'_' in s.get('set_status','') for f in ('chambers','cloister','ring'))]
                    if doors:chapel_fixture=(state,observed,doors[0])
                if vault_fixture is None and floor==2 and any(s.get('tooltip')=='Vault Seal' for s in ss):vault_fixture=(state,floor)
                if run==1:
                    desired=('gallery','barracks') if floor==2 else ('chambers','cloister','ring')
                    chests=[s for s in ss if s.get('tooltip')=='Treasure Chest' and any('_complex_'+f+'_' in s.get('set_status','') for f in desired)]
                    if chests:
                        x,y=map(int,chests[0]['location'].split(',')[:2]);cx,cy=(x//36)*36+18,(y//36)*36+18;c=terrain(observed)['collision']
                        candidates=[(xx,yy) for yy in range((y//36)*36,(y//36+1)*36) for xx in range((x//36)*36,(x//36+1)*36) if c[yy][xx]==0]
                        px,py=min(candidates,key=lambda p:(p[0]-cx)**2+(p[1]-cy)**2)
                        console(f'/intramap={px},{py} restore=hpmp');screenshot(f'floor-{floor}-close.png')
            halt()
        assert chapel_fixture is not None,'No inner chapel was generated for native QA'
        state,old,door=chapel_fixture;restore_fixture(state,'chapel')
        first=dump('chapel-closed.txt');ss=parse(state/(MAP_HASH[3]+'.txt'));x,y=map(int,door['location'].split(',')[:2])
        chest=next(s for s in ss if s.get('tooltip')=='Treasure Chest' and tuple(int(v)//36 for v in s['location'].split(',')[:2])==(x//36,y//36))
        stand=press(door,terrain(first));opened=dump('chapel-open.txt')
        assert not neighbours(chest,reachable(terrain(first)['collision'],stand)),'Chapel reward bypassed its door'
        assert neighbours(chest,reachable(terrain(opened)['collision'],stand)),'Door did not open the inner chapel'
        console('/save_game=true')
        assert door['set_status'] in flags(),'Door state was not saved'
        halt();start('chapel-reload');again=dump('chapel-reload.txt')
        assert all(terrain(opened)[k]==terrain(again)[k] for k in ('background','background_fringe','object','topology','collision')),'Chapel or loop changed on reload'
        report['inner_chapel_click_and_reload']=True
        (out/'native-report.json').write_text(json.dumps(report,indent=2)+'\n')
        assert vault_fixture is not None,'No cavern vault was generated for native QA'
        state,floor=vault_fixture;restore_fixture(state,'cavern-vault');ss=parse(state/(MAP_HASH[floor]+'.txt'))
        seals=sorted([s for s in ss if s.get('tooltip')=='Vault Seal'],key=lambda s:s['set_status'])
        gate=next(s for s in ss if s.get('activate')=='static' and '_complex_vault_' in s.get('set_status',''))
        coords=[tuple(map(int,m.split(',')[1:3])) for m in gate['mapmods'] if m.startswith('collision,')]
        before=dump('cavern-vault-closed.txt');press(seals[0],terrain(before));one=dump('cavern-vault-one.txt')
        assert seals[0]['set_status'] in flags() and gate['set_status'] not in flags()
        assert all(terrain(one)['collision'][yy][xx]==1 for xx,yy in coords)
        press(seals[1],terrain(one));two=dump('cavern-vault-open.txt')
        assert gate['set_status'] in flags() and all(terrain(two)['collision'][yy][xx]==0 for xx,yy in coords)
        halt();start('cavern-vault-reload');again=dump('cavern-vault-reload.txt')
        assert all(terrain(two)[k]==terrain(again)[k] for k in ('background','background_fringe','object','topology','collision')),'Cavern vault changed on reload'
        report['cavern_two_seals_and_reload']=True;halt()
        # Isolate delivered modules only for overview photographs. Their geometry
        # is the same data used by the normal procedural generator.
        for floor,family in [(1,'cloister'),(2,'gallery'),(3,'chambers')]:
            data_root(f'overview{floor}');save.mkdir(parents=True)
            relative=f'maps/iron_labyrinth/exploration/f{floor}/complex_{family}_1.txt'
            c=layers(parse(ROOT/'diantre'/relative))['collision']
            candidates=[(xx,yy) for yy,row in enumerate(c) for xx,t in enumerate(row) if t==0]
            px,py=min(candidates,key=lambda p:(p[0]-18)**2+(p[1]-18)**2)
            text=re.sub(r'^spawn=.*$',f'spawn={relative},{px},{py}',template,flags=re.M)
            text=re.sub(r'^campaign=.*$','campaign=diantre_town_hamlet_forest',text,flags=re.M)
            (save/'avatar.txt').write_text(text);(save/'stash_HC.txt').write_text('')
            start(f'overview{floor}',overview=True);console('toggle_hud');screenshot(f'floor-{floor}-overview.png');halt()
        report.update(fresh_floors=len(records),distinct_structures=len({r['collision_sha256'] for r in records}),
                      mandatory_gate_checks=sum(r['mandatory_gates'] for r in records),
                      runtime_loops=[r['runtime_loops'] for r in records],source='live native layers and collider')
        (out/'native-results.json').write_text(json.dumps(records,indent=2)+'\n')
        (out/'native-report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps({'output':str(out),**report}),flush=True)
    finally:
        halt();xvfb.terminate();xvfb.wait(timeout=10)
        for f in logs:f.close()
        # All observations are written before deleting disposable test saves.
        for path in out.glob('userdata-*'):shutil.rmtree(path)


if __name__=='__main__':main()
