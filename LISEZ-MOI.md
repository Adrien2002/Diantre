# Diantre 0.5.1 — hameau compact et salles rapprochées

Le hameau forestier est assemblé par Flare à chaque nouvelle partie. Quatre
quartiers carrés de 12 × 12 cases sont choisis et disposés parmi leurs variantes.
Chaque partie conserve exactement les sept marchands. L’entrée reste au nord ;
les maisons, leur longueur et les affectations des marchands varient.

Les quartiers étaient de 18 × 18 dans la version précédente. Leur réduction
rapproche les deux rangées de commerces. La lisière garde une marge devant les
marchands, et les toits sont séparés de la paroi rocheuse. La falaise monte hors
champ, sans plateau horizontal dessiné au-dessus des arbres.

## Jouer

Placer le dossier `diantre` dans le dossier `mods` de Flare, puis activer Diantre.
Le moteur doit fournir son mod `default`. Les ressources nécessaires d’Empyrean
sont incluses. Version minimale du moteur : 1.14.280 ; essais sous 1.15.86.

Créer une nouvelle partie pour obtenir les nouveaux placements et les nouvelles
salles. Les cartes déjà générées sont conservées dans les sauvegardes : une
mise à jour ne les redessine pas. Les anciennes palettes de ville restent
lisibles ; le retour utilise l’entrée propre à la ville de la partie.

## Donjons

Les trois étages actuels conservent leurs salles circulaires, basilicales,
cryptes, galeries, grandes salles et chambres à levier. Leurs modules passent
de 48 × 48 à 36 × 36 cases en retirant une marge rocheuse de six cases de chaque
côté. Les grandes pièces voisines peuvent ainsi se rejoindre par une ouverture
courte. Les pièces plus petites conservent des couloirs.

Les sorties non choisies par le générateur restent fermées. Les portes à clé,
les portes ordinaires, les leviers et leurs états sauvegardés sont conservés.
Les faces noires des murs générés sont remplacées par des blocs natifs dont
les deux faces visibles sont texturées. Les images d’origine ne sont pas
retouchées.

Il s’agit toujours d’un assemblage de modules Flare. Une génération de salles
et de passages aussi libre que celle d’Angband demanderait un autre générateur ;
ce changement rapproche les salles existantes sans prétendre le reproduire.

## Développement et validation

Les fichiers `.txt` sont directement utilisables par Flare. Python sert
uniquement aux outils de développement :

```sh
python3 tools/build_surface.py
python3 tools/refine_dungeons.py
python3 tools/check_surface.py
python3 tools/check_dungeons.py
```

Le premier contrôle examine 4 096 combinaisons de quartiers et de marchands :
accès, empreintes des maisons, retrait des toits, fermeture du périmètre et
emprise des arbres devant les marchands. Le second examine les 135 modules de
salle et leurs raccords, les interactions, les coordonnées et l’impossibilité
de contourner une porte verrouillée. Les comptes et essais en jeu figurent
dans `docs/VALIDATION-surface.md`.

Les stocks et l’équilibrage des combats ne sont pas modifiés. Les autres biomes
naturels restent à définir ensemble. Le travail se poursuit directement sur
`main`, sans branche de développement supplémentaire.

## Références et ressources

L’organisation de la surface s’inspire de `town_gen_layout`, `get_lot_bounds`
et `build_store` dans le code d’Angband, au commit
`e473720ed88a0f0c7ca66815cef3000eb4a38bc3` :
https://github.com/angband/angband/blob/e473720ed88a0f0c7ca66815cef3000eb4a38bc3/src/gen-cave.c

Les principes sont adaptés ; le code C n’est pas copié. Les cabanes utilisent
l’assemblage natif de Black Oak City. Les licences et attributions des ressources
Flare/Empyrean restent dans `diantre/licenses` et `ASSET_MANIFEST.json`.
