# Diantre 0.5.0 — hameau forestier compact

La surface des nouvelles parties reprend les principes de la ville d’Angband :
une entrée au nord, un massif infranchissable, des commerces disposés sur des
parcelles et des rues qui restent accessibles. Les sept marchands occupent de
véritables cabanes en bois. Une lisière épaisse délimite la clairière ; les
caisses et les tables ne servent plus de bordure.

Cette première déclinaison est forestière. Les autres biomes naturels seront
définis avec la même organisation, après examen de ce premier résultat.

## Jouer

Placer le dossier `diantre` dans le dossier `mods` de Flare, puis activer Diantre.
Le moteur doit fournir son mod `default`, comme pour toute installation Flare.
Les ressources nécessaires d’Empyrean sont déjà incluses.

Créer une nouvelle partie pour obtenir le nouveau hameau. Les anciennes cartes
de surface restent présentes pour que les sauvegardes existantes retrouvent
leur ancienne ville. Le retour du donjon conserve le hameau de la partie.

## Génération

Flare assemble à l’exécution quatre modules carrés de 18 × 18 cases, choisis
parmi des variantes. Deux familles de marchés ne peuvent être choisies qu’une
fois : chaque partie conserve exactement les sept marchands.

Le terrain complet mesure 44 × 44 cases, contre 88 × 88 auparavant. Le massif,
son entrée et les accès principaux sont fixes ; les parcelles, les cabanes et
la répartition des marchands changent. Les bosquets occupent les parcelles
secondaires, et les enseignes indiquent les commerces au survol.

Les fichiers `.txt` sont directement utilisables par Flare. Python est seulement
un outil de développement :

```sh
python3 tools/build_surface.py
python3 tools/check_surface.py
```

Le contrôle parcourt les 4 096 combinaisons possibles de modules et vérifie les
accès aux marchands, au coffre et à l’entrée, ainsi que les empreintes des
cabanes, l’impossibilité de passer derrière le massif et la fermeture du
périmètre. Il ne remplace pas l’examen visuel en jeu.

## Références

Le code d’Angband consulté est `src/gen-cave.c`, fonctions `town_gen_layout`,
`get_lot_bounds` et `build_store`, au commit
`e473720ed88a0f0c7ca66815cef3000eb4a38bc3` :
https://github.com/angband/angband/blob/e473720ed88a0f0c7ca66815cef3000eb4a38bc3/src/gen-cave.c

Les principes d’organisation sont adaptés ; le code C n’a pas été copié.
L’assemblage des cabanes suit les tuiles natives employées dans Black Oak City
par Empyrean. Les graphismes ne sont pas modifiés ; leurs licences et
attributions sont conservées dans `diantre/licenses` et `ASSET_MANIFEST.json`.

Les stocks des marchands et les cartes des donjons ne sont pas modifiés dans
cette refonte de surface. Les faces noires des murs du donjon restent à revoir.
