# Diantre 0.8.7 — persistance des cartes et entrée réorientée

Diantre conserve ses trois étages procéduraux de 5 × 5 secteurs, leurs
combats à difficulté fixe, les escaliers visibles (0.8.4), le coffre
près des cabanes (0.8.6) et le premier portail permanent à l'étage 2
(0.8.5). Aucun changement n'a été apporté à ces mécaniques de combat.

La **0.8.7** traite trois régressions observées en jeu :

- **Carte régénérée après la mort :** le démarrage utilise désormais
  un délai de 350 ms après la première sauvegarde, afin de laisser
  Flare créer le répertoire de cache du personnage avant la
  première génération. L'entrée du donjon applique également
  une sauvegarde avant son chargement différé de 250 ms.
- **Marchands disparus :** les variantes de maisons possédaient des
  marqueurs de sélection persistants. En cas de régénération,
  ces marques pouvaient éliminer les deux familles intermédiaires
  et ne laisser que **trois des sept marchands**. Elles sont
  désormais effacées après la génération, avant les sorties et
  lors des retours vers le village. Les variantes restent uniques
  pendant leur assemblage.
- **Entrée de mine :** suppression du sprite 228 dont la porte
  violette était orientée vers le mauvais côté, remplacement
  par la variante native 224, et restauration de la continuité
  de la falaise à droite. Le passage et son déclencheur sont
  inchangés. Le coffre reste en (7,9), près des maisons.

**Contrôles statiques : réussis** sur GitHub Actions, dont 23 040
configurations de modules, 4 096 compositions du village et
1 832 vérifications de fichiers. **À confirmer en jeu :** les
cache de cartes persistent réellement après une mort / résurrection,
les sept vendeurs restent présents au retour, et le nouveau visuel
d'entrée correspond bien à une ouverture vers le nord.

Pour vérifier les changements, utiliser **un nouveau personnage**.
Les fichiers de cartes précédemment enregistrés dans des sauvegardes
anciennes ne sont pas écrasés par la mise à jour : ne supprimez pas les
anciennes sauvegardes pour tester.

Voir [le rapport 0.8.7](docs/VALIDATION-persistance-0.8.7.md),
[le bilan 0.8.6](docs/VALIDATION-hameau-0.8.6.md)
et [les portails 0.8.5](docs/VALIDATION-portails-0.8.5.md).

## Trois environnements actuels

| Étage | Environnement | Architecture et détails |
| --- | --- | --- |
| 1 | Ruines anciennes | Dalles fissurées, cours, grandes salles et colonnes |
| 2 | Cavernes enfouies | Sol de terre, rochers, lobes irréguliers, tunnels sinueux et galeries portant des rails |
| 3 | Cryptes de pierre | Dallages sombres, nefs, chapelles fermées dans de grandes salles, statues, monuments et braseros |

Ces ambiances utilisent les images natives de Flare sans les modifier.
Les cryptes conservent les blocs de maçonnerie complets des ruines pour leurs
limites ; leurs sols et leur mobilier proviennent du donjon natif. Les pièces
de mur ayant des faces arrière noires sont écartées des limites isolées.

Les formes intérieures des cavernes et des cryptes sont produites par des
règles différentes. La génération conserve la grille de secteurs de Flare et
la collection de variantes calculées avant le jeu ; elle ne crée pas encore
librement toute la géométrie de l’étage pendant la partie.

## Génération des donjons

À chaque nouvelle carte, Flare assemble des ensembles de pièces et construit
la progression vers la sortie. Le générateur repère ensuite les sorties
inutilisées de secteurs voisins appartenant au même palier de progression.
Il choisit au hasard au moins une liaison supplémentaire lorsqu’un raccord
sûr existe, puis peut en ajouter d’autres. Ces boucles offrent des itinéraires
alternatifs tout en gardant les portes à clé obligatoires.

Les nouveaux secteurs comprennent des chambres jointives, des galeries, des
embranchements, des passages décalés et des circuits autour d’une cour ou d’un
massif. Des grandes salles ponctuelles apportent un contraste avec ces espaces
plus divisés. Les trois étages actuels disposent de 96 variantes générées,
réparties entre huit familles d’ensembles de pièces.

Une chambre forte facultative demande d’actionner deux mécanismes situés dans
des pièces différentes. Les mécanismes restent accessibles avant l’ouverture,
et la récompense est séparée des sorties et des clés de progression. Le coffre,
les portes et les mécanismes ont leurs propres états.

Les nouvelles liaisons sont tirées au sort par Flare une seule fois pour la
carte. Les décisions sont sauvegardées et les mêmes passages sont rétablis lors
d’un retour ou d’une reprise de partie. Python n’est pas nécessaire pour jouer.
Le moteur Flare standard suffit ; aucun moteur particulier n’est livré avec
le mod.

## Installer et tester

Placer le dossier `diantre` dans le dossier `mods` de Flare, puis activer Diantre.
Le moteur doit fournir son mod `default`. Les ressources nécessaires d’Empyrean
sont incluses. Flare 1.15 ou ultérieur est requis.

Créer une nouvelle partie pour examiner la nouvelle génération. Flare conserve
les cartes déjà générées dans les sauvegardes. Le hameau forestier, les sept
marchands et le retour vers la ville restent disponibles.

Les ennemis actuels ont leurs caractéristiques natives fixes ; leur difficulté
ne dépend pas du niveau du héros. La progression prévue sur vingt étages, avec
un boss tous les cinq étages, est décrite dans
[`docs/PROGRESSION-fixe.md`](docs/PROGRESSION-fixe.md), avec le catalogue de
référence d’Empyrean. Les vingt étages et leurs boss restent à intégrer.

## Développement

Les données de jeu sont des fichiers natifs Flare. Les outils Python génèrent
les variantes et les scripts, puis vérifient les raccords, les interactions et
les règles de progression :

```sh
python3 tools/build_exploration.py
python3 tools/check_exploration.py
python3 tools/check_population.py
python3 tools/check_themes.py
python3 tools/check_encounters.py
```

`tools/check_exploration.py --help` décrit aussi le contrôle d’un export d’état
du moteur, associé à son cache de carte et à la sauvegarde de test. Le contrôle
porte sur le terrain et distingue les occupants temporaires des obstacles.

Les anciens outils de surface et de validation restent disponibles. Le bilan
de la correction architecturale 0.8.2 est dans
[VALIDATION-architecture-0.8.2.md](docs/VALIDATION-architecture-0.8.2.md), et le bilan
de densité 0.8.1 dans [VALIDATION-densite-0.8.1.md](docs/VALIDATION-densite-0.8.1.md). Les essais
effectués réellement avec Flare dans VALIDATION-grands-etages.md concernent
la version 0.8.0, pas la 0.8.1. Le contrôle des pixels des palettes demande
Pillow pendant le développement. Le travail reste directement sur main.

## Architecture et ressources

La génération utilise encore la grille de secteurs native de Flare. Chaque
secteur peut contenir plusieurs pièces ; les variantes sont construites par
les outils du mod, puis combinées dans le jeu. Les connexions supplémentaires
sont choisies pendant la partie par les événements natifs du moteur.

L’organisation du hameau s’inspire des principes de la ville d’Angband étudiés
dans `src/gen-cave.c`, au commit `e473720ed88a0f0c7ca66815cef3000eb4a38bc3` :
https://github.com/angband/angband/blob/e473720ed88a0f0c7ca66815cef3000eb4a38bc3/src/gen-cave.c

Le code C d’Angband n’est pas repris. Les graphismes natifs Flare/Empyrean ne sont
pas retouchés. Les licences, attributions et empreintes des fichiers restent
dans `diantre/licenses` et `diantre/ASSET_MANIFEST.json`.
