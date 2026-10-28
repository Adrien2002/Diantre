# Project direction

Diantre takes its exploration and progression cues from Angband and Diablo 1,
using Flare and Empyrean's freely licensed assets.

The intended world contains a small town, limited in scope like Diablo 1's,
and a single explorable dungeon. Both the town and dungeon floors are
procedural. Authored chunks provide building blocks for the native generator;
their assembly defines the playable map.

Custom quests will complement exploration in the spirit of Diablo 1.
Empyrean's campaign and storyline are outside this scope.

The prototype currently generates a safe town when a character is created.
It is a single open square with a clear central plaza. Two merchants each have
their own house, and the dungeon entrance stands a little apart in a hillside.
Buildings and scenery must not divide the surface into rooms or forest corridors.
Their lots vary around the square, leaving broad approaches between services.
The town also contains a shared stash. Ten settings
use the available asset families: conifer forest, broadleaf woodland, rocky
terrain, marsh, meadow, riverside, snow, cave, ruins and citadel. The layout and
entrance position vary between characters and persist in their saves.

Town and dungeon generation run in the engine using reusable chunks. Custom
quests and a longer progression remain to be implemented.
