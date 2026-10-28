#!/usr/bin/env python3
"""Exercise new games and a surface/dungeon round trip in the unmodified engine."""
import hashlib
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import tempfile
from map_data import sections, town_details
import sys

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "tools"))
from build_town import BIOMES
BASELINE_ERRORS = {
    f"ERROR: ItemStack: Item id is {item}, but quantity is zero."
    for item in (753, 2000, 2001, 2002)
} | {
    "ERROR: SDLSoftwareRenderDevice: Couldn't load image: "
    "'images/menus/game_over.png'. SDL_RWFromFile(): No file or no mode specified"
}


def run_game(work, hook, label, reload=False, script=None, click=None, language="en"):
    config = work / "config" / "flare"
    config.mkdir(parents=True, exist_ok=True)
    (config / "settings.txt").write_text(
        "resolution_w=1674\nresolution_h=960\nfullscreen=0\nrenderer=sdl\n"
        f"hwsurface=0\nvsync=0\ntexture_filter=0\nlanguage={language}\n"
        "setup_language=1\nsetup_mousemove=1\npause_on_focus_loss=0\n"
    )
    data = work / "data"
    data.mkdir(exist_ok=True)
    env = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy",
               XDG_CONFIG_HOME=str(work / "config"), XDG_DATA_HOME=str(data),
               LD_PRELOAD=str(hook), DIANTRE_SCREENSHOT=str(work / f"{label}.bmp"))
    if reload:
        env["DIANTRE_RELOAD"] = "1"
    else:
        env.pop("DIANTRE_RELOAD", None)
    if click:
        env["DIANTRE_CLICK"] = click
    else:
        env.pop("DIANTRE_CLICK", None)
    args = ["sh", str(PROJECT / "tools/play.sh"), "--renderer=sdl", "--no-audio"]
    if reload:
        args.append("--load-slot=1")
    if script:
        args.append("--load-script=" + script)
    log_path = work / f"{label}.log"
    with log_path.open("w") as log:
        subprocess.run(args, env=env, stdout=log, stderr=subprocess.STDOUT,
                       check=True, timeout=60)
    log = log_path.read_text()
    active = next(line for line in log.splitlines() if "Active mods:" in line)
    assert "diantre (" in active and "fantasycore" not in active and "empyrean_campaign" not in active, active
    errors = [line for line in log.splitlines() if "ERROR:" in line]
    known = [line for line in errors if "/npcs/il_loren.txt:11] StatBlock: "
             "'vendor_ratio_buy' is not a valid key." in line]
    unexpected = [line for line in errors if line not in BASELINE_ERRORS and line not in known]
    if language != "en":
        expected = f"ERROR: MessageEngine: Unable to find '{language}' in engine/languages.txt. Falling back to 'en'."
        assert expected in unexpected, "Language restriction did not apply"
        unexpected.remove(expected)
    assert not unexpected, (log_path, unexpected)
    assert re.search(r"^language=en$", (config / "settings.txt").read_text(), re.M)
    assert "Map: Loading map 'maps/arrival.txt'" not in log
    assert "Map: Loading map 'maps/perdition_harbor.txt'" not in log
    assert (work / f"{label}.bmp").stat().st_size > 100_000
    assert not (data / "flare/saves/empyrean").exists()
    save = data / "flare/saves/diantre/1"
    avatar = (save / "avatar.txt").read_text()
    spawn = re.search(r"^spawn=(.*)$", avatar, re.M)[1].split(",")
    caches = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in (save / "maps").glob("*.txt")}
    towns = [p for p in (save / "maps").glob("*.txt")
             if "scripts/town/enter_dungeon.txt" in p.read_text()]
    for town in towns:
        town_details(town)
    print(f"PASS {label}: {spawn[0]}, {len(errors)} expected diagnostics", flush=True)
    return {"log": log, "spawn": spawn, "caches": caches, "towns": towns, "avatar": avatar, "save": save}


def main():
    cflags = shlex.split(os.environ.get("SDL_CFLAGS", ""))
    if not cflags:
        cflags = shlex.split(subprocess.check_output(["pkg-config", "--cflags", "sdl2"], text=True))
    artifacts = PROJECT / ".runtime/tests"
    artifacts.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="smoke-", dir=artifacts))
    print(f"Artifacts: {work}", flush=True)
    hook = work / "driver.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-Wall", "-Wextra",
                    "-Werror", *cflags, str(PROJECT / "tests/drive_flare.c"),
                    "-ldl", "-o", str(hook)], check=True)
    first = run_game(work / "first", hook, "new-game")
    second = run_game(work / "second", hook, "new-game")
    assert first["spawn"][0].startswith("maps/town/") and second["spawn"][0].startswith("maps/town/")
    assert len(first["towns"]) == len(second["towns"]) == 1
    a, b = [town_details(r["towns"][0]) for r in (first, second)]
    assert a["header"]["procgen_chunks"] != b["header"]["procgen_chunks"], "Repeated layout"
    resumed = run_game(work / "first", hook, "reload", reload=True)
    assert resumed["caches"] == first["caches"], "Reload changed the town"
    assert "Generated main path" not in resumed["log"]
    dungeon = run_game(work / "first", hook, "descend", reload=True, script="scripts/town/enter_dungeon.txt")
    assert dungeon["spawn"][0] == "maps/iron_labyrinth_f1.txt"
    assert len(dungeon["caches"]) == 2, "Exactly one town and one dungeon floor"
    returned = run_game(work / "first", hook, "return", reload=True, script="scripts/town/return.txt")
    assert returned["spawn"][0] == first["spawn"][0], "Return changed the biome"
    assert returned["caches"] == dungeon["caches"], "Round trip changed cached maps"
    assert tuple(map(int, returned["spawn"][1:3])) == a["exit"], "Return did not use the cave mouth"
    assert "Generated main path" not in returned["log"]
    # At the saved cave exit the mouth is (+0.5, -1) tiles from the hero.
    # With 192x96 isometric tiles and this viewport, its centre is (981,456).
    clicked = run_game(work / "first", hook, "click-entry", reload=True, click="981,456")
    assert clicked["spawn"][0] == "maps/iron_labyrinth_f1.txt", "Click did not activate the cave hotspot"
    assert clicked["caches"] == returned["caches"]
    english = run_game(work / "first", hook, "english-only", reload=True, language="fr")
    assert english["caches"] == clicked["caches"], "Language fallback changed map caches"
    # Exercise every biome, independently of the randomly selected starting one.
    for biome in BIOMES:
        case = work / biome
        shutil.copytree(work / "second", case)
        avatar = case / "data/flare/saves/diantre/1/avatar.txt"
        if second["spawn"][0] != f"maps/town/{biome}.txt":
            # New maps use the generated start chunk. A previously generated
            # map must retain its saved position, not the template's (8,10).
            avatar.write_text(re.sub(r"^spawn=.*$", f"spawn=maps/town/{biome}.txt,8,10",
                                     avatar.read_text(), flags=re.M))
        result = run_game(case, hook, biome, reload=True)
        assert result["spawn"][0] == f"maps/town/{biome}.txt"
        assert f"diantre_town_{biome}" in result["avatar"]
        assert any(town_details(p)["header"]["title"] == BIOMES[biome].title for p in result["towns"])
    print(f"PASS: {len(BIOMES)} procedural biomes, accessible unique dungeon entrance and vendors, "
          "varied layouts, isolated saves, preserved town and dungeon after round trip.")


if __name__ == "__main__":
    main()
