# Diantre 0.8.4 — étage compact et escalier de descente reconnaissable

Date : 31 octobre 2026. **Statut : cartes régénérées, tests statiques
réussis et publication sur main. Tests natifs 0.8.4 non effectués.**

## Retour de jeu à l'origine de cette passe

Après environ 30 minutes d'exploration de la 0.8.3, le joueur a signalé
qu'un étage de donjon était devenu trop vaste et difficile à parcourir
avec la seule minimap ; la sortie d'étage, bien qu'interactive, était
pratiquement impossible à distinguer parmi les dalles et piliers.

## Cause réelle de la descente invisible

Les cartes de référence `maps/iron_labyrinth/f1/end.txt`,
`f2/end.txt` et `f3/end.txt` possèdent chacune **cinq tuiles** de
l'escalier descendant dans la couche `background` :

- étage 1 : **349, 350, 351, 352, 353** ;
- étage 2 : **344, 345, 346, 347, 348** ;
- étage 3 : **349, 350, 351, 352, 353**.

Les modules historiques de génération `maps/iron_labyrinth/generated/f*/end.txt`
conservaient le hotspot `Stairs Down` / `Return to Town` (3 × 3 cases),
mais avaient perdu ces tuiles de fond. Dans les modules d'exploration
0.8.3, des blocs de maçonnerie recouvraient également ce centre.
**Ce n'était donc pas seulement un manque de contraste : le véritable
dessin de l'escalier avait disparu.**

## Corrections implémentées

### Descente

`tools/build_exploration.py` contient `restore_native_stairs`, invoqué
lors de l'installation de chaque module `procgen_type=end`. Il :

1. lit le motif de cinq tuiles dans la carte d'origine du même étage ;
2. vérifie l'identité et les dimensions de ce motif ;
3. dégage un voisinage de **5 × 5** cases autour du hotspot, sans modifier
   l'événement de transition ni son identifiant de point de retour ;
4. restitue le motif d'escalier natif et les collisions correspondant au
   bâti de la descente, en laissant les cases adjacentes accessibles.

Le contrôle `tools/check_exploration.py` vérifie les cinq tuiles,
l'absence d'obstacle graphique dans la zone dégagée, l'empreinte de
collision et le point de retour `stairs_down` pour chaque étage.

### Surface et cheminement

| Paramètre | 0.8.3 | 0.8.4 |
| --- | ---: | ---: |
| Grille de secteurs | 6 × 6 (36) | **5 × 5 (25)** |
| Emprise générée | 216 × 216 | **180 × 180** |
| Dimensions du fichier de carte (avec marges) | 232 × 232 | **196 × 196** |
| Longueur paramétrée du chemin principal | 26–30 | **18–21** |
| Rencontres ordinaires par secteur | 11–19 ennemis | **inchangées** |
| XP individuelles des ennemis | 2 / 4 / 8 | **inchangées** |

La grille perd 11 secteurs potentiels (environ **30,6 %**). La réduction
des cases totales de génération est du même ordre. Ce n'est pas une
réduction uniforme du nombre réel d'ennemis : le total dépendra du nombre
de secteurs effectivement occupés par Flare, des tirages et des portes.

`tools/check_population.py` emploie désormais un seuil minimal
d'observation proportionné à la longueur du parcours, plutôt que
l'ancien minimum arbitraire de 210 ennemis applicable à la grande grille.
Le calcul statique vérifie toujours les seuils cumulatifs des niveaux 2,
3 et 4 sur la base des ennemis potentiellement accessibles.

## Publications et contrôles

- [09c8402](https://github.com/Adrien2002/Diantre/commit/09c8402a1cde65be871dd084ed37c8db06d2a6fb) : modifications du
  générateur, de la validation et de la version 0.8.4.
- [GitHub Actions 41232344130](https://github.com/Adrien2002/Diantre/actions/runs/41232344130) : **réussite**
  des générations et tests statiques.
- [5591f2c](https://github.com/Adrien2002/Diantre/commit/5591f2c91f6368edb8809027d0e751244a27db4c) : cartes
  et fichiers de données régénérés, publiés sur `main`.

Résultats relevés : **23 040** configurations de raccords des
modules, **96** formes de collision distinctes, **567** identifiants
d'état contrôlés, **1 829** empreintes de ressources vérifiées et
**4 096** assemblages du hameau. Les contrôles de population
confirment des minima théoriques d'environ **142 / 142 / 166 ennemis**
selon les étages avant XP, sans prétendre mesurer des apparitions
réelles dans le moteur.

Vérification directe des trois modules `exploration/f*/end.txt` :
les cinq tuiles du bon étage sont présentes, avec la zone de 5 × 5 cases
dégagée et sans sprite de pilier, les escaliers restant infranchissables
mais interactifs depuis leur périphérie.

## Risques non écartés / validation à poursuivre

- **Aucun nouveau personnage n'a été lancé** dans le moteur Flare par
  cette campagne ; la qualité du visuel et le ressenti sur la durée ne
  sont donc pas encore confirmés.
- Les nouveaux paramètres de longueur réduisent l'espace de recherche ;
  le moteur peut se comporter différemment suivant les graines,
  notamment en nombre de tentatives, de branches ou de secteurs.
- L'accès aux clés, passages et interactions a été contrôlé sur les
  modules, pas sur une campagne native 0.8.4 de cartes complètes.
- L'escaliers est plus concret graphiquement mais les couleurs restent
  celles des tuiles originales ; un repère supplémentaire pourrait
  rester nécessaire après examen des captures.

Faire une **nouvelle partie** pour comparer : temps de parcours, nombre
de secteurs occupés, longueur des détours, combats par minute, repérage
immédiat de la descente, rechargement des cartes et accès par clés.
Ne pas utiliser les sauvegardes personnelles pour des tests automatiques.
