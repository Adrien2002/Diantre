# Diantre 0.8.1 — bilan de la première densification

Date : 31 octobre 2026. **Prototype généré et vérifié statiquement ; aucune
validation native ou partie intégrale n'a encore été effectuée en 0.8.1.**

## Pourquoi cette passe

Les captures de Diantre 0.8.0 montraient de grands espaces peu habités et un
placement facilement prévisible : deux poches de trois à quatre ennemis par
secteur ordinaire. Cette étape augmente la population et change sa répartition
sans modifier les XP, les graphismes natifs, le niveau fixe des ennemis ou le
moteur Flare. Voir également l'étude de DevilutionX du 31 octobre.

## Modification effectivement livrée

- **Population** : dans tools/build_exploration.py, encounter_groups calcule
  un budget de 11–19 ennemis pour chaque complexe ordinaire, à partir de la
  surface admissible et d'une petite variation de graine. Il produit plusieurs
  rectangles 5 × 5 non superposés, dont des solitaires et des groupes de 2,
  3 ou 4. La présence d'au moins un solitaire et d'un groupe de trois est
  vérifiée. Les rectangles sont pré-calculés par variante ; le moteur Flare
  choisit les positions concrètes à l'intérieur de chacun.
- **Sécurité des apparitions** : le générateur exclut les cases solides,
  protégées et les portions qui seraient condamnées par un raccord natif.
  Le contrôle de population vérifie les capacités après les variantes de
  raccord, le nombre et le non-recouvrement des régions.
- **Décoration** : dans tools/dungeon_themes.py, add_details peut maintenant
  placer jusqu'à 11 obstacles décoratifs natifs par complexe, au lieu de 4,
  dans des emplacements ouverts d'au moins 5 × 5 cases.
- **Progression** : catégories et spawn_level=default inchangés. Les XP
  individuelles sont toujours 2/4/8 sur les trois profondeurs actuelles.
- **Publication** : tools, settings version 0.8.1 et données régénérées sur
  la branche main. Un workflow GitHub Actions reconstruit, vérifie et publie
  les données générées, uniquement si les contrôles statiques réussissent.

## Validation réellement exécutée

Source : [commit 18c265e](https://github.com/Adrien2002/Diantre/commit/18c265e1b1a3d4d8c080c74e13937c47d364aebd).
Campagne : [GitHub Actions, exécution 41207699702](https://github.com/Adrien2002/Diantre/actions/runs/41207699702), conclusion **success**.
Données générées : [commit d3d59d5](https://github.com/Adrien2002/Diantre/commit/d3d59d5228f17f5512e5a7d96b22660ad2b02f64) (105 fichiers modifiés).

Les commandes build_exploration.py, check_exploration.py,
check_population.py, check_themes.py et check_encounters.py ont réussi.
Les journaux confirment 96 complexes, 23 040 configurations de raccords
testées, 96 formes de collision, 627 noms d'état contrôlés et 1 829
empreintes de fichiers vérifiées.

Le total d'obstacles décoratifs des **32 variantes de complexes de chaque
environnement** vaut 181 pour les ruines, 191 pour les cavernes et 192 pour
les cryptes. Ces sommes portent sur le catalogue, et **pas** sur un étage
généré dans une partie.

| Profondeur | Ennemis théoriques min.–max. | XP théoriques min.–max. |
| --- | ---: | ---: |
| 1 | 230–619 | 460–1 238 |
| 2 | 230–619 | 920–2 476 |
| 3 | 250–619 | 2 000–4 952 |

**Ces intervalles sont des bornes combinatoires**, pas des comptages de
monstres apparus. Les trente cartes natives de 0.8.0 ne valident pas ces
valeurs de 0.8.1. Une forte augmentation d'XP totale ne prouve pas à elle
seule que le rythme de combat et d'exploration soit devenu plaisant.

## Vérifications qui restent nécessaires

1. Exécuter Flare standard sur de nouvelles sauvegardes de laboratoire et
   mesurer population apparue, accessibilité, XP, passages, mécanismes et
   rechargements. Garder les sauvegardes personnelles hors des tests.
2. Jouer plusieurs passages et mesurer les distances sans rencontre, la
   distribution perçue des groupes, l'acquisition réelle d'XP et l'effort
   de combat.
3. Revoir les captures de murs et piliers. Les faux passages et les parties
   architecturales suspendues **ne sont pas encore corrigés**.
4. Ajouter de vrais détails thématiques (barils, sarcophages, mobilier et
   éléments non bloquants) après étude des tuiles et de leurs collisions.

Les variations de géométrie restent contraintes par la grille de secteurs
de Flare ; aucun générateur global de Diablo n'a été porté.
