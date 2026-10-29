# Flare / Empyrean assets redistributed with Diantre

Source: https://github.com/flareteam/flare-game

Upstream revision: `af6eee6d339ac98011864bfe89da837fe7769c28`

Flare: Empyrean Campaign is Copyright ©2010-2013 Clint Bellanger.
Contributors retain copyrights to their original contributions.
See `CREDITS.txt` for the upstream authors and `README-upstream.md` for the
original copyright and licensing statement.

Art and game data are licensed under Creative Commons Attribution-ShareAlike
3.0 Unported; later versions are permitted by upstream. The complete license
is in `LICENSE-CC-BY-SA-3.0.txt`. Diantre's game data use CC-BY-SA-3.0.

Font software keeps its separate SIL Open Font License 1.1. The complete license,
copyright notices and reserved font names are in `LICENSE-FONTS-OFL.txt`.
The redistributed font binaries have not been modified.

Diantre changes: selects the Iron Labyrinth and shared game resources from
`fantasycore` and `empyrean_campaign`; combines layered text files according to
Flare's APPEND rules; starts new characters in a generated town; separates saves;
redirects exits and recall scrolls to the saved town; excludes the room
that sends the player into Empyrean's quest maps and its developer campaign tome.
The fixed boss chasm is omitted; the last generated floor returns to the town.
No fixed town or other campaign maps are included. New reusable surface chunks
provide ten biome/atmosphere variants. Tile IDs from the snow, cave, ruins and
dungeon atlases are offset into a shared palette; their images are unmodified.
The seven town merchant profiles adapt Empyrean's names, appearances and shop
stock. Campaign dialogue, quest requirements and quest-gated stock are removed;
Loren uses the Iron Labyrinth stock with the default shop pricing. Each merchant
has a separate house and is placed exactly once in a newly generated town.
Dungeon generation now uses new 48-tile architectural sectors with twelve room
families, varied corridors, native key gates and lever-operated treasure vaults.
The ruins atlas and stair/gate sprites remain unchanged. Original dungeon chunks
and their dependencies are retained for compatibility with previously saved maps.

`../../ASSET_MANIFEST.json` records the selected files, source mod(s), changes,
sizes and SHA-256 hashes. Binary art/audio/font files are copied without changes.
Files under `campaign/diantre` in the project contain Diantre overrides and adapted game data.

The engine and its `default` mod are supplied separately by Flare and keep their
own licenses; they are not redistributed inside Diantre.
