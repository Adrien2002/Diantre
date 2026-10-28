# Diantre

Diantre is a standalone Flare campaign inspired by Angband and Diablo 1. A small
procedural town leads to a single explorable dungeon, the **Iron Labyrinth**.
Flare's native generator assembles the town and dungeon floors from reusable
chunks. Generated layouts belong to the character's save and persist when
reloading or returning to the surface.

## Installation

The mod includes its game data, artwork, animations, sounds, music and fonts.
It requires a recent Flare engine and the engine's `default` mod.

If Flare is installed at `~/Games/Flare/flare`, with its default mod at
`~/Games/Flare/mods/default`, run:

```sh
sh tools/play.sh
```

For another installation directory:

```sh
FLARE_HOME=/path/to/Flare sh tools/play.sh
```

`FLARE_BINARY` and `FLARE_DEFAULT` select the executable and default mod separately.
The launcher stages `default` and `diantre` in `.runtime/game`. Diantre's assets
are bundled in this repository; installing Empyrean or fantasycore is unnecessary.

For manual installation, copy `mods/diantre` into Flare's `mods` directory and
select **Diantre** under **Configuration → Mods**. The engine loads `default`
automatically. Start a new game to discover the town.

Tested engine: `flareteam/flare-engine` revision
`b436611c8c6e9baf7af2c5b9f1e483c6b28b08c3` (1.15.82).
The declared minimum is 1.14.280; Debian's 1.14 package predates the generator
used by this mod.

## Current prototype

- A safe procedural town with two merchants and a shared stash.
- Ten randomly selected environments: conifer forest, broadleaf woodland, rocky
  terrain, marsh, meadow, riverside, snow, cave, ruins and citadel.
- Random town layouts, scenery variants and a single dungeon entrance, connected
  to the character's spawn point by a walkable path. Click the entrance to descend.
- The cave mouth opens into the foot of a three-tier hillside. Successively
  smaller terraces rise behind the entrance, with a clear approach at ground
  level. The entrance cliff spans two wall sections so its terrain lip sits
  above the cave arch. Snow biomes use matching snow-covered cliffs and terraces.
- Three generated Iron Labyrinth floors, using Empyrean's classes, equipment,
  monsters and summoning mechanics.
- Surface exits, return portals and recall scrolls lead back to the dungeon
  entrance in the same town. The third floor's exit also returns to town.

The biome is selected when creating a character and remains part of that save.
Saves are stored separately from Empyrean under `saves/diantre`.

Start a new game when upgrading to version 0.3. Older cached maps retain the
exits from the version that generated them; they are not migrated automatically.
Town scenery updates also appear in new games; existing saves keep their cached
surface layout.
Custom quests, an endless dungeon and further balance work remain planned.
See [project direction](docs/DIRECTION.md).

## Assets and licenses

Assets come from `flareteam/flare-game`, revision
`af6eee6d339ac98011864bfe89da837fe7769c28`. The bundled selection is approximately
**398 MiB**. It follows game-file references, random monster categories, equipment
animations and implicit engine resources. Complete equipment and power catalogs
are retained for their dynamic dependencies.

Artwork and game data use **CC-BY-SA-3.0**. Fonts retain their separate
**SIL OFL 1.1** license. Full credits, licenses and modification notices are
included in [licenses/flare-game](mods/diantre/licenses/flare-game/NOTICE.md) and
must accompany redistributions. Diantre's tools use the MIT license; see
[LICENSE](LICENSE). The separately supplied engine retains its own licenses.

`mods/diantre/ASSET_MANIFEST.json` records imported files, provenance, modifications,
sizes and SHA-256 hashes. Binary assets are copied without modification. Town
palettes combine the original atlases using distinct tile IDs.

## Development

Custom data lives in `campaign/diantre`. Rebuild the reusable town chunks with:

```sh
python3 tools/build_town.py
```

This authors mod data; Flare performs the random selection and assembly at
runtime. No complete playable town map has a fixed layout.

To reproduce asset extraction from local sources at the revision listed above:

```sh
python3 tools/import_assets.py \
  --source /path/to/flare-game \
  --default /path/to/Flare/mods/default \
  --output .runtime/new-extraction/diantre
```

The importer requires an empty output directory. Compare its output before
replacing the mod to preserve changes made since extraction. Game data can be
edited directly in `mods/diantre`; the asset audit reports changes to imported
file hashes.

Translations follow [Flare's native gettext workflow](docs/LOCALIZATION.md).

## Validation

On Linux, with Python 3, a C compiler and SDL2 development headers:

```sh
FLARE_HOME="$HOME/Games/Flare" python3 tests/assets.py
python3 tests/town.py
python3 tests/translations.py
FLARE_HOME="$HOME/Games/Flare" python3 tests/smoke.py
```

The asset audit checks bundled files, dependencies and licenses. Terrain checks
cover 1,950 chunk and connector combinations. The engine test creates two
characters, checks distinct layouts, reloads a save, descends into the dungeon
and returns to the same town entrance without regenerating either map. It also
checks all ten environments, entrance access, merchants and the entrance's
click interaction.

The tests use real game scripts and generated collision data. Captures, logs and
test saves stay in `.runtime/tests`, separate from player saves. The UI driver
uses a 1674 × 960 viewport. In the prepared cloud environment:

```sh
FLARE_HOME=/workspace/flare-tools/current \
LD_LIBRARY_PATH=/workspace/flare-tools/root/usr/lib/x86_64-linux-gnu \
SDL_CFLAGS='-I/workspace/flare-tools/root/usr/include/SDL2 -I/workspace/flare-tools/root/usr/include/x86_64-linux-gnu' \
python3 tests/smoke.py
```

Validation also ran with an engine directory containing only `flare` and
`mods/default`. Headless software rendering supports automated checks;
interactive play requires a graphical display.

The tested upstream revisions emit diagnostics about zero quantities for some
items and a missing `images/menus/game_over.png`. These were also reproduced
with unmodified Empyrean. Loren may emit a `vendor_ratio_buy` diagnostic: the
NPC loader supports the field, but its stat validator reports it as unknown.
Tests retain these known diagnostics and reject other errors, including failed
map-cache writes or blocked spawn points. They do not replace a full playthrough.
