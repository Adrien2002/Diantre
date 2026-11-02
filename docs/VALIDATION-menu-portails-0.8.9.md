# Diantre 0.8.9 — retirer l'étage 1 des téléporteurs

## Comportement demandé

Les téléporteurs servent à rejoindre les étages pairs préalablement
découverts. L'étage 1, accessible directement depuis le village, ne
doit jamais apparaître dans une liste de destinations de portail.

## Modification

- `npcs/diantre_waypoint_town.txt` : retrait de `response=floor_1`
  et du dialogue correspondant. L'étage 2 est toujours conditionné
  à `diantre_waypoint_f2`.
- `npcs/diantre_waypoint_f2.txt` : même retrait, tout en préservant
  les choix `Woodland Hamlet`, `Level 2` et `Cancel`.
- `tools/check_waypoints.py` : vérification explicite de l'absence
  de `floor_1` et de toute transition vers `iron_labyrinth_f1.txt`.
  Le contrôle conserve les vérifications des déclencheurs, du statut
  permanent, des arrivées et des destinations autorisées.
- Version déclarée : 0.8.9.

Le portail du village reste visible même avant la découverte du
premier portail profond. Tant que celui de l'étage 2 n'est pas
déverrouillé, le menu ne présente aucune destination d'étage ;
seule l'option `Cancel` est disponible.

Aucun changement à la génération des niveaux, à leur persistance
ou aux conditions de progression.

## Validation

La régénération GitHub Actions reconstruit les fichiers et vérifie
leur manifeste d'empreintes. Le contrôle du menu ne remplace pas
un essai natif de dialogue après déverrouillage de l'étage 2.
