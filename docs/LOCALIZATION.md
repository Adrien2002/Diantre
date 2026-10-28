# Localization

Diantre uses Flare's `MessageEngine` and its supported subset of gettext.
Source strings remain in the game data and serve as message IDs. Display names,
dialogue, descriptions and tooltips can be translated independently of file
names and internal biome identifiers.

## File layout

- `engine/languages.txt` declares available languages using `<code>=<name>` entries.
- `languages/data.pot` contains the mod's source-message template.
- `languages/data.<code>.po` contains a translation of the mod's messages.
- `languages/engine.<code>.po`, supplied by the engine's `default` mod, translates
  Flare's shared interface.

## Updating the template

After changing game text, run:

```sh
python3 tools/update_translations.py
```

A template entry follows Flare's native convention:

```po
msgid "Dungeon Entrance"
msgstr ""
```

Copy the template to `data.<code>.po` and fill in `msgstr`. Keep `msgid` and any
format placeholders unchanged, then add the language to the mod's language
table. Flare reads `.po` files directly; compiling them to `.mo` is unnecessary.

## Separate language packs

A language pack can depend on `diantre`, use the same `game=diantre` family and
provide its own `languages/data.<code>.po`. Its `engine/languages.txt` can extend
the language table with an `APPEND` directive. This keeps translations separate
from the engine and source game data.

## Upstream references

- [Flare translation documentation](https://github.com/flareteam/flare-engine/blob/master/docs/translations.html)
- [Flare data-string extractor](https://github.com/flareteam/flare-engine/blob/master/tools/localization/xgettext.py)
