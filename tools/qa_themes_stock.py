#!/usr/bin/env python3
"""Smoke-test the three environments with an unmodified native Flare engine.

Uses the extracted Xvfb/xdotool dependencies from qa_themes_native.py's lab.
Creates a character via the UI, clicks the hamlet entrance, loads the deeper
floors via the developer console and invokes the normal town-return script.
This is a compatibility smoke test, not a complete manual playthrough.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

from check_surface import parse
from dungeon_themes import THEMES


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lab',type=Path,required=True)
    p.add_argument('--engine-repo',type=Path,required=True)
    a=p.parse_args();lab=a.lab.resolve();engine=a.engine_repo.resolve()
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=engine),'Engine must be unmodified'
    out=lab/('stock-'+str(time.time_ns()));out.mkdir()
    config=out/'config/flare';config.mkdir(parents=True)
    data=out/'userdata';data.mkdir();save=data/'flare/saves/diantre/1'
    (config/'settings.txt').write_text('fullscreen=0\nresolution_w=1280\nresolution_h=720\nmin_render_size=960\nmax_render_size=960\nrenderer=sdl\nmouse_move=1\ndev_mode=1\ndev_hud=0\nlanguage=en\nsetup_language=1\nsetup_mousemove=1\npause_on_focus_loss=0\n')
    env=os.environ.copy();env.update(DISPLAY='127.0.0.1:99',LD_LIBRARY_PATH=str(lab/'sysroot/usr/lib/x86_64-linux-gnu'),XDG_CONFIG_HOME=str(out/'config'),XDG_DATA_HOME=str(data))
    logs=[];game=None
    def logfile(name):
        f=(out/name).open('w');logs.append(f);return f
    xvfb=subprocess.Popen([str(lab/'sysroot/usr/bin/Xvfb'),':99','-screen','0','1280x720x24','-nolisten','local','-nolisten','unix','-listen','tcp','-ac'],env=env,stdout=logfile('xvfb.log'),stderr=subprocess.STDOUT)
    def inp(*args):subprocess.run([str(lab/'sysroot/usr/bin/xdotool'),*map(str,args)],env=env,check=True,timeout=20)
    def click(x,y):
        inp('mousemove',x,y,'mousedown',1);time.sleep(.15);inp('mouseup',1)
    def console(text):
        inp('key','--delay',180,'F5');time.sleep(.15);inp('type','--delay',45,text)
        inp('key','--delay',180,'Return');time.sleep(.15);inp('key','--delay',180,'F5')
        inp('keyup','Shift_L','Shift_R','Control_L','Control_R');time.sleep(1)
    def avatar():return dict(line.split('=',1) for line in (save/'avatar.txt').read_text().splitlines() if '=' in line)
    report={'engine_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=engine).decode().strip(),'engine_unmodified':True,'floors':[]}
    try:
        time.sleep(1)
        game=subprocess.Popen([str(lab/'build/flare'),'--data-path='+str(lab/'game'),'--mods=diantre','--renderer=sdl','--no-audio'],env=env,cwd=out,stdout=logfile('game.log'),stderr=subprocess.STDOUT)
        time.sleep(7);assert game.poll() is None
        click(830,498);time.sleep(3);click(760,168);time.sleep(.5);click(354,691);time.sleep(4)
        assert (save/'avatar.txt').exists(),'Character creation failed'
        console('/save_game=true');town=avatar()
        assert town['spawn'].startswith('maps/town/hamlet_forest.txt,')
        assert 'diantre_town_hamlet_forest' in town['campaign'].split(',')
        report['native_character_and_hamlet']=True
        console('/intramap=12,4');click(712,324);time.sleep(3)
        console('/save_game=true');assert avatar()['spawn'].startswith('maps/iron_labyrinth_f1.txt,')
        report['hamlet_entrance_clicked']=True
        for floor in range(1,4):
            if floor>1:console(f'/intermap=maps/iron_labyrinth_f{floor}.txt,-1,-1,stairs_up')
            console('/save_game=true');assert avatar()['spawn'].startswith(f'maps/iron_labyrinth_f{floor}.txt,')
            cache=save/'maps'/(str(7811557995279168839+(floor-1)*268435456)+'.txt')
            header=next(s for s in parse(cache) if s['section']=='header')
            assert header['tileset']==THEMES[floor]['palette']
            report['floors'].append({'floor':floor,'palette':header['tileset']})
        console('/script=scripts/town/return.txt');console('/save_game=true')
        assert avatar()['spawn'].startswith('maps/town/hamlet_forest.txt,')
        assert 'diantre_town_hamlet_forest' in avatar()['campaign'].split(',')
        report['return_to_same_hamlet']=True
        shutil.copyfile(save/'avatar.txt',out/'final-avatar.txt')
        (out/'stock-report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps({'output':str(out),**report}),flush=True)
    finally:
        if game and game.poll() is None:game.terminate();game.wait(timeout=10)
        xvfb.terminate();xvfb.wait(timeout=10)
        for f in logs:f.close()
        shutil.rmtree(data)


if __name__=='__main__':main()
