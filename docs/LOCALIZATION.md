# Localisation

Le programme est en anglais uniquement pendant le développement. Les textes
anglais restent les chaînes source dans les fichiers de jeu ; ils passent par
le `MessageEngine` de Flare, qui utilise un sous-ensemble de gettext.
Il n'y a pas de traduction intégrée aux images ni de verrou dans le code C++.

Le schéma natif est conservé :

- `engine/languages.txt` déclare les langues disponibles ; actuellement `en=English`.
- `languages/data.pot` est le modèle contenant les chaînes source du mod.
- `languages/data.<code>.po` contiendra ultérieurement une traduction du mod.
- `languages/engine.<code>.po`, dans le mod `default` du moteur, fournit les
  traductions de l'interface commune de Flare.

Régénérer le modèle après avoir changé les textes :

```sh
python3 tools/update_translations.py
```

Une entrée suit exactement la convention de Flare :

```po
msgid "Dungeon Entrance"
msgstr ""
```

Le traducteur copie le modèle vers `data.<code>.po`, remplit `msgstr`, conserve les
`msgid` anglais et les paramètres de formatage, puis ajoute `<code>=<language name>`
dans la table de langues du mod. Les fichiers `.po` sont lus directement par Flare,
sans compilation en `.mo`. Le prototype ne fournit actuellement aucun `.po`.

Un pack de langue séparé peut aussi dépendre de `diantre`, appartenir à la même
famille `game=diantre`, fournir son `languages/data.<code>.po` et étendre la table
avec un fichier `engine/languages.txt` commençant par `APPEND`. Ce mécanisme
n'exige pas de modifier le moteur ni les fichiers de jeu anglais.

Références amont :

- [Documentation des traductions de Flare](https://github.com/flareteam/flare-engine/blob/master/docs/translations.html)
- [Extracteur des données de Flare](https://github.com/flareteam/flare-engine/blob/master/tools/localization/xgettext.py)

Les noms de fichiers et identifiants de biomes restent stables et non traduits.
Les noms affichés, dialogues, descriptions et infobulles sont traduisibles.
