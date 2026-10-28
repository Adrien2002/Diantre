# Diantre

Prototype de campagne Flare inspirée d'Angband et de Diablo 1 : après la création
du personnage, une petite ville procédurale donne accès à un unique donjon,
le **Labyrinthe de fer**. La ville et les étages sont assemblés par le générateur
natif de Flare. Leurs plans appartiennent à la sauvegarde et restent identiques
quand on reprend la partie ou remonte à la surface.

**Le programme est exclusivement en anglais pour le moment.** La table de langues
du mod limite les choix à `English` ; une ancienne préférence différente revient
à l'anglais. La documentation de développement reste en français.
Le mécanisme natif gettext est conservé : un modèle `languages/data.pot` prépare
les traductions futures, sans activer de traduction maintenant. Voir
[la documentation de localisation](docs/LOCALIZATION.md).

## Installation autonome

`mods/diantre` contient maintenant les données, images, animations, sons, musiques
et polices nécessaires au prototype. **Empyrean et fantasycore ne sont plus des
mods requis.** Seuls le moteur Flare récent et son mod système `default` sont
nécessaires. Le moteur C++ n'est pas modifié.

Avec le moteur dans `~/Games/Flare/flare` et son mod `~/Games/Flare/mods/default` :

```sh
sh tools/play.sh
```

Autre emplacement :

```sh
FLARE_HOME=/chemin/vers/Flare sh tools/play.sh
```

`FLARE_BINARY` et `FLARE_DEFAULT` permettent de choisir séparément le binaire et
le mod système du moteur. Le lanceur assemble uniquement `default` et `diantre`
dans `.runtime/game`. Les assets de Diantre sont des fichiers dans ce dépôt,
sans liens vers l'installation d'Empyrean.

Installation manuelle : copier `mods/diantre` dans le dossier `mods` du moteur,
puis activer seulement `diantre` ; `default` est chargé automatiquement.

Référence testée : moteur `flareteam/flare-engine` à la révision
`b436611c8c6e9baf7af2c5b9f1e483c6b28b08c3` (1.15.82). Minimum déclaré : 1.14.280.
Le paquet Debian 1.14 est trop ancien pour la génération utilisée ici.

## Contenu de cette étape

- Trois étages générés du Labyrinthe de fer, avec les classes, objets et monstres
  d'Empyrean ; les combinaisons d'équipement et les invocations sont conservées.
- Départ dans une petite ville sûre, avec deux marchands et un coffre partagé.
- Dix biomes/ambiances sélectionnés aléatoirement : conifères, feuillus, rochers,
  marais, prairie, rives, neige, caverne, ruines et citadelle. L'agencement, les
  morceaux de décor et la position de l'entrée du donjon sont aussi tirés au sort.
- Une seule entrée de donjon par ville, reliée à la place d'arrivée par un chemin
  accessible. Cliquer sur son point d'interaction pour descendre au premier étage.
- Aucune carte fixe de la campagne d'origine. La salle de boss fixe et la salle
  qui téléportait vers les quêtes d'Empyrean sont exclues.
- Les anciennes sorties, les portails de retour et le parchemin de rappel
  ramènent à la bouche du donjon dans la même ville. La sortie du troisième étage
  fait de même. Changer de biome exige une nouvelle partie, pas une simple visite.

Les sauvegardes sont séparées d'Empyrean dans `saves/diantre` ; aucune n'est effacée.
Commencer une nouvelle partie avec la version 0.3 pour découvrir la ville.
Les anciennes cartes mises en cache conservent les sorties de la version qui
les a générées ; le mod ne les efface pas et ne les migre pas automatiquement.
Le prototype ne propose pas encore un donjon infini ni ses propres quêtes.
L'équilibrage nécessite des essais de jeu. Voir [la direction du projet](docs/DIRECTION.md).

## Origine, licences et extraction

Les ressources proviennent de `flareteam/flare-game`, révision
`af6eee6d339ac98011864bfe89da837fe7769c28`. L'ensemble importé représente environ
**398 Mio**. La sélection suit les références des fichiers de jeu, les catégories
aléatoires de monstres, les animations d'équipement et les ressources implicites
utilisées par le moteur. Il ne s'agit pas d'une minimisation de chaque objet ou
pouvoir individuel.

Les illustrations et données sont sous **CC-BY-SA-3.0** ; les polices gardent leur
licence **SIL OFL 1.1**. Les crédits complets, licences et changements sont fournis
avec le mod dans [licenses/flare-game](mods/diantre/licenses/flare-game/NOTICE.md).
Ces fichiers doivent accompagner toute redistribution du mod. Le moteur reste
sous ses propres licences. Les outils de Diantre sont sous MIT, voir `LICENSE`.

`mods/diantre/ASSET_MANIFEST.json` décrit les fichiers importés, leur provenance,
leurs modifications, leur taille et leur empreinte SHA-256. Les binaires sont
copiés sans modification. `campaign/diantre` conserve les données propres à Diantre.
Les palettes de ville réunissent les atlas d'origine avec des identifiants de
tuile distincts, sans modifier les images.

`python3 tools/build_town.py` reproduit les variantes de morceaux de ville. Ce
script sert à créer les données du mod ; il n'est pas lancé pendant le jeu.
Au démarrage d'une nouvelle partie, Flare choisit le biome et assemble les morceaux.
Les morceaux sont prédéfinis, mais aucune carte de ville complète n'est fixe.

Pour reproduire l'extraction depuis les sources locales à la révision indiquée :

```sh
python3 tools/import_assets.py \
  --source /chemin/vers/flare-game \
  --default /chemin/vers/Flare/mods/default \
  --output .runtime/nouvelle-extraction/diantre
```

L'importeur refuse un dossier de sortie non vide. Comparer le résultat avant de
remplacer le mod, afin de préserver les modifications de jeu faites depuis
l'extraction. Les données de jeu peuvent être modifiées directement dans `mods/diantre`.
L'audit des empreintes signale alors les fichiers modifiés depuis l'import initial.

## Vérification

Sur Linux, avec Python 3, un compilateur C et les en-têtes SDL2 :

```sh
FLARE_HOME="$HOME/Games/Flare" python3 tests/assets.py
python3 tests/town.py
python3 tests/translations.py
FLARE_HOME="$HOME/Games/Flare" python3 tests/smoke.py
```

L'audit contrôle les fichiers embarqués, leurs références et leurs licences.
Le contrôle de terrain parcourt 1 950 combinaisons de variantes et de passages.
Le test du moteur crée deux personnages, vérifie des plans distincts, reprend
une sauvegarde, descend dans le donjon puis revient à la même entrée de ville
sans régénérer les plans. Il charge également chacun des dix biomes, contrôle
l'unicité et l'accessibilité de l'entrée ainsi que les deux marchands.
Les transitions utilisent les scripts de jeu, et l'accessibilité est contrôlée
sur les collisions réellement générées. Il exige que les mods actifs
soient indépendants de `fantasycore` et d'`empyrean_campaign`. Les captures, journaux
et sauvegardes restent dans `.runtime/tests`, sans toucher aux parties du joueur.

Le pilote utilise les menus anglais et la résolution 1674 × 960. Dans le cloud :

```sh
FLARE_HOME=/workspace/flare-tools/current \
LD_LIBRARY_PATH=/workspace/flare-tools/root/usr/lib/x86_64-linux-gnu \
SDL_CFLAGS='-I/workspace/flare-tools/root/usr/include/SDL2 -I/workspace/flare-tools/root/usr/include/x86_64-linux-gnu' \
python3 tests/smoke.py
```

Les tests ont aussi été exécutés avec un dossier moteur ne contenant que `flare`
et `mods/default`. Le rendu sans affichage permet les contrôles ; jouer demande
un affichage local.

Les révisions amont émettent déjà des diagnostics sur des quantités nulles pour
certains objets et une image `images/menus/game_over.png` absente. Ces messages ont
été reproduits avec Empyrean seul. Le marchand Loren peut produire un diagnostic
`vendor_ratio_buy` : son chargeur de PNJ reconnaît ce champ, mais la validation de
ses statistiques le signale comme inconnu. Le test conserve ces messages et
rejette toute autre erreur, notamment un échec d'enregistrement du plan ou une
apparition dans un mur. Les tests ne remplacent pas un parcours de jeu complet.
