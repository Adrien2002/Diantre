# Diantre 0.8.2 — correction des fausses surfaces praticables

Date : 31 octobre 2026.

**Statut : correction intégrée et contrôles statiques réussis. Pas encore validée visuellement dans Flare standard sur une nouvelle partie.**

## Signalement du joueur

Deux captures prises dans les ruines anciennes montraient des trous apparents dans les murs, des dalles ressemblant à des sols accessibles au-delà des bordures et des zones que le personnage ne pouvait pas franchir malgré leur apparence. La minimap montrait les contours sinueux de ces masses.

Il s'agissait d'un problème distinct de la densité des ennemis modifiée en 0.8.1.

## Cause identifiée dans les fichiers

- Dans `Complex.build()` de `tools/build_exploration.py`, chaque case hors des couloirs et salles praticables recevait une collision solide : **1** sur le contour, **3** à l'intérieur de la masse.
- Les contours utilisaient l'objet graphique de maçonnerie **144**, mais les masses intérieures utilisaient les sprites **153–160**.
- Dans les palettes natives de Diantre, les sprites 153–160 étaient des **tuiles de sol déplacées verticalement d'environ 190 pixels**, visuellement semblables à des dalles élevées. Le joueur pouvait donc voir des surfaces planes qui ressemblaient à une continuation du chemin alors qu'elles appartenaient aux cases **collision=3**.
- Les anciens modules, modules spéciaux et bandes de raccord `links_*` héritaient de la même représentation. Ne corriger que `Complex.build()` aurait laissé des défauts aux jonctions entre secteurs.
- Les identifiants **136–151** utilisent également un même bloc de maçonnerie complet dans la palette des ruines. Il s'agit d'une représentation simple et répétitive, pas d'une famille complète d'angles et de murs correctement raccordés.

**Mesure illustrative avant correction :** `complex_cloister_1.txt` à l'étage 1 comportait **544** cases avec `collision=3` et un sprite de sol surélevé 153–160. `links_0.txt` comportait **900** cases de même nature dans sa carte source. Ces chiffres décrivent des modules de 36 × 36 cases, **pas** une carte complète réellement générée en jeu.

## Correction produite

- `Complex.build()` utilise un véritable bloc de maçonnerie **144** pour les cases solidement bloquées, qu'elles soient au bord ou au cœur d'une masse.
- `install_copy()` remplace les sprites de sol surélevé **153–160** par la maçonnerie **144** uniquement pour les cases `collision=3`, y compris dans les salles historiques et les raccords de secteurs.
- Les collisions sont **inchangées** : il s'agit d'une correction de la représentation des obstacles, pas d'un changement de traversabilité ou de logique des clés.
- `tools/check_themes.py` vérifie maintenant que **chaque case `collision=3` de chaque module actif**, y compris les raccords, emploie un sprite de masse maçonnée (136–151). Cela évite de réintroduire des surfaces planes dans les obstacles cachés.
- Les textures graphiques de Flare n'ont pas été modifiées.

## Vérifications réellement effectuées

Code source publié : [7e591dd](https://github.com/Adrien2002/Diantre/commit/7e591dd539a71927a96bf9a748d9adbca6efd0d6).

GitHub Actions : [exécution 41210485887](https://github.com/Adrien2002/Diantre/actions/runs/41210485887), génération et contrôles statiques **réussis**. Données régénérées : [3fd87b5](https://github.com/Adrien2002/Diantre/commit/3fd87b50585ec4835f12e55f10186bbcc31e6a12) ; **141 fichiers** modifiés.

Les contrôles ont notamment vérifié 96 complexes, **23 040 configurations de raccords**, les accès aux pièces fermées, la présence et la validité des tuiles, la cohérence du nouveau traitement des masses solides et les 1 829 empreintes du manifeste.

Contrôle direct des fichiers publiés :

| Module | Cases avec collision=3 | Cases utilisant désormais la maçonnerie | Incohérences restantes pour cette règle |
| --- | ---: | ---: | ---: |
| Ruines, complex_cloister_1 | 544 | 544 | 0 |
| Ruines, links_0 | 900 | 900 | 0 |
| Cavernes, complex_gallery_0 | 459 | 459 | 0 |
| Cryptes, complex_ring_2 | 480 | 480 | 0 |

## Limites explicites

- **Aucune capture native post-correction n'a encore été inspectée.** L'assertion garantit qu'une case solide n'est plus représentée par une dalle surélevée, mais ne prouve pas à elle seule l'absence de trous *visuels* entre sprites de maçonnerie.
- Les bords sont encore construits avec un bloc de pierre répété ; il manque une véritable sélection des murs, retours, coins et piliers en fonction du voisinage.
- Ce correctif ne fait pas disparaître la **grille des secteurs** de Flare ; il ne concerne pas non plus les interruptions de raccords ou le calcul de la population des monstres.
- Une forte densité de blocs peut aussi rendre certains espaces visuellement lourds ou masquer le personnage à l'écran : **à évaluer dans le moteur**, sans annoncer la correction esthétique comme définitivement achevée.

## Étape de validation suivante

Créer **une nouvelle partie** avec les fichiers à jour (Flare conserve les anciennes cartes en cache dans les sauvegardes). Revenir aux mêmes types de jonctions et de massifs et réaliser des captures à la caméra normale ; vérifier : continuité des murs, correspondance entre passages visibles et collisions, angles de pièces, visibilité du personnage. Si la répétition des blocs reste visible, développer une passe dédiée de raccords de maçonnerie et des tests par voisinage plutôt que de rajouter des piliers arbitraires.
