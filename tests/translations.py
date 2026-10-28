#!/usr/bin/env python3
"""Check the native gettext template and English-only runtime data."""
import ast
from pathlib import Path
import sys

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "tools"))
from build_town import BIOMES
from update_translations import catalog
from import_assets import translation_catalogs


def main():
    mod = PROJECT / "mods/diantre"
    template = (mod / "languages/data.pot").read_text()
    assert template == catalog(mod), "Translation template is stale"
    messages = {ast.literal_eval(line[6:]) for line in template.splitlines() if line.startswith("msgid ")}
    for text in [*(b.title for b in BIOMES.values()), "Lysa, Provisions", "Borin, Equipment",
                 "Udana, Metalworker", "Florin, Apothecary", "Yora, Enchanter", "Abasi, Traveling Merchant",
                 "Bakat, Goblin Packrat", "Martigan", "Loren, Undead Trader",
                 "Dungeon Entrance", "Shared Stash", "Return to Town"]:
        assert text in messages, f"Missing translatable string: {text}"
    assert not list((mod / "languages").glob("*.po")), "No active translated catalogs yet"
    assert "en=English" in (mod / "engine/languages.txt").read_text()
    examples = ["languages/data.fr.po", "languages/data.de.po"]
    assert translation_catalogs(examples, "en=English\n") == []
    assert translation_catalogs(examples, "en=English\nfr=French\n") == ["languages/data.fr.po"]
    print(f"PASS: {len(messages)-1} English msgids in the native gettext template; no active translations.")


if __name__ == "__main__":
    main()
