# Diantre 0.8.3 — finition du hameau forestier

Date : 31 octobre 2026. Statut : **fichiers régénérés et tests statiques
réussis**, rendu natif à confirmer sur une nouvelle partie.

## Signalements

Deux captures du hameau montraient une entrée minière visuellement
recouverte par la roche et une toiture de cabane donnant l'impression
d'un raccord interrompu. Les problèmes concernent la carte de ville, pas
les donjons remaniés en 0.8.2.

## Vérifications du code et corrections

- Dans `tools/build_surface.py`, le hameau superposait 16 couches de falaise
  sur la rangée y=2. L'entrée minière native est l'objet 228 en (12,2),
  avec un hotspot d'interaction en (12,3). La **première couche de falaise**
  est désormais dégagée en (12,2), derrière le portail, sans retirer
  la roche des côtés ni les 15 couches supérieures, ni changer les collisions.
- Les cabanes utilisent les sprites 208, 209, 210, 211. L'étude directe de
  la carte native `flareteam/flare-game`, `black_oak_city.txt`, révision
  `af6eee6d339ac98011864bfe89da837fe7769c28`, confirme que le bâtiment
  à cette orientation utilise une seule tuile de milieu 210.
  `build_surface.py` ajoutait parfois une seconde tuile 210 pour créer
  une variante plus longue, avec un risque de couture de toit perceptible.
  Les cabanes reviennent au motif exact 208/209/210/211.
- `tools/check_surface.py` vérifie désormais les quatre pièces des
  cabanes, interdit les tuiles 210 orphelines ou répétées et vérifie
  la découpe de la falaise derrière l'entrée, les couches conservées
  au-dessus, l'objet 228 et l'accès au hotspot.
- Le workflow GitHub Actions exécute maintenant `build_surface.py` et
  `check_surface.py` lors des changements de générateur du hameau.
- Aucun fichier PNG natif de Flare n'a été retouché. Les portes, les
  marchands, les inventaires, les statistiques et le donjon sont inchangés.

## Commits et validation

- [142164c](https://github.com/Adrien2002/Diantre/commit/142164c95ffd4d5a762366f2e2f8b0b662c1733f) : correctifs du
  générateur et ajouts de contrôles, poussés sur `main`.
- [GitHub Actions, exécution 41215269126](https://github.com/Adrien2002/Diantre/actions/runs/41215269126) : génération et contrôles statiques réussis.
- [25c209e](https://github.com/Adrien2002/Diantre/commit/25c209ef591d4b2d5a475efbefa94cc78be63c95) : fichiers générés,
  16 fichiers modifiés, publiés sur `main`.
- Le contrôle du hameau a validé **4 096 configurations d'assemblage**,
  pour **64 dispositions** de tuiles distinctes. Les contrôles statiques
  des étages précédents ont également réussi.

## Limites et prochain examen

Les tests vérifient la structure, les couches, les entrées, les collisions
et l'accessibilité, **pas** l'absence définitive de couture visible dans
le moteur. La présence d'un dégagement derrière le portail est validée
au niveau des données, mais l'esthétique finale dépend du rendu des sprites
et de l'ordre exact de dessin.

Tester avec un **nouveau personnage ou une sauvegarde jetable neuve**,
car Flare conserve les cartes procédurales dans ses sauvegardes.
Inspecter une cabane au nord, une cabane au sud et la mine en vue normale.
Si la toiture apparaît toujours coupée, capturer le bâtiment en entier
pour déterminer s'il s'agit de la jonction native des quatre sprites
plutôt que de l'ancienne répétition de tuile.
