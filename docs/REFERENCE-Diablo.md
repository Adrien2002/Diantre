# Référence de conception : Diablo et grands étages

Référence utilisée pour la 0.8.0. Les résultats d’essais sont consignés dans
[`VALIDATION-grands-etages.md`](VALIDATION-grands-etages.md).

## Observation de la référence

Lecture de DevilutionX, révision
`06d17533e6469fdafaac724bcb36c4b69b71a273`, port moderne de Diablo.

- [`Source/levels/drlg_l1.cpp`](https://github.com/diasurgical/DevilutionX/blob/06d17533e6469fdafaac724bcb36c4b69b71a273/Source/levels/drlg_l1.cpp)
  construit des chambres puis des pièces adjacentes de dimensions variables.
  La cathédrale est régénérée tant que son emprise minimale n’est pas atteinte
  (533 cases de structure au premier étage, 693 au deuxième, 761 ensuite).
- [`Source/monster.cpp`](https://github.com/diasurgical/DevilutionX/blob/06d17533e6469fdafaac724bcb36c4b69b71a273/Source/monster.cpp),
  `InitMonsters`, calcule une population supplémentaire à partir des cases non
  solides (`na / 30`), avec des plafonds et des cas particuliers. Le placement
  ordinaire emploie des individus au premier étage, puis des petits groupes
  pouvant compter deux à trois ou trois à cinq monstres selon le contexte.
  `PlaceGroup` contrôle l’occupation des cases et la région de placement.

Ces nombres ne se transposent pas directement aux cases, à la vitesse et aux
statistiques de Flare. Le principe retenu pour Diantre est une grande surface
effective, des lieux nombreux, des groupes locaux modestes et un budget total
de rencontres mesuré sur l’étage. Aucun code ni graphisme de Diablo n’est repris.

## Application réalisée et limites

- Étendre la région de génération de 4 × 4 à 6 × 6 secteurs de 36 cases, soit
  216 × 216 cases et 2,25 fois l’emprise précédente.
- Allonger le parcours principal et les ramifications pour employer cette
  emprise, avec les liaisons supplémentaires et les portes à clé existantes.
- Répartir les rencontres des complexes en petits groupes dans des zones
  distinctes, avec des passages et des espaces de respiration entre eux.
- Garder les récompenses d’XP et les caractéristiques fixes des ennemis pendant
  les essais, afin de mesurer l’effet de la surface et des rencontres ajoutées.
- Mesurer la population, l’XP accessible et les seuils de niveau sur des cartes
  fraîches. Distinguer les budgets théoriques des apparitions réellement exportées.

La grille de secteurs reste celle du moteur Flare standard. Cet agrandissement
ne remplace pas encore son assemblage par un générateur de géométrie libre à
l’échelle de tout l’étage. La cible à vingt étages et ses quatre boss reste un
travail distinct des trois étages actuellement intégrés.
