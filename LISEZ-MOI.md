# Diantre 0.6.0 — donjons à parcours variables

Le cœur du mod est la qualité de la génération : varier les espaces, les
parcours et les découvertes entre les parties. Les formes de salles restent
libres de changer au fil du développement.

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
```

`tools/check_exploration.py --help` décrit aussi le contrôle d’un export d’état
du moteur, associé à son cache de carte et à la sauvegarde de test. Le contrôle
porte sur le terrain et distingue les occupants temporaires des obstacles.

Les anciens outils de surface et de validation des modules d’origine restent
disponibles. Les résultats des essais sont consignés dans
`docs/VALIDATION-generation.md`. Le travail se poursuit directement sur `main`.

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
