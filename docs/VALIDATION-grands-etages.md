# Validation de Diantre 0.8.0 — 31 octobre 2026

Les données de jeu testées sont celles de
`6f67ee5d969e64184c009c167dc4120765638414`. Les recherches, les corrections et
les résultats intermédiaires ont été publiés progressivement sur `main`.

## Surface et répartition des rencontres

La région procédurale passe de 144 × 144 à 216 × 216 cases, soit de 16 à 36
secteurs possibles et 2,25 fois l’emprise. Le parcours principal configuré
compte 26 à 30 secteurs. Les ramifications et les raccords supplémentaires
développent les itinéraires autour de cette progression.

Chaque secteur ordinaire possède deux zones éloignées de 7 × 7 cases, avec
trois à quatre ennemis chacune. Leurs centres sont distants d’au moins 18 cases.
Les variantes des salles à clé gardent leurs groupes particuliers de quatre
à sept ennemis ; les sorties possèdent deux petits groupes de un à deux.
Une zone de rencontre ne doit pas être confondue avec une salle entière :
plusieurs groupes peuvent être attirés ensemble par les actions du joueur.

Les XP par ennemi restent à 2, 4 et 8 dans les trois profondeurs. Les statistiques
et les apparitions ne s’adaptent pas au personnage. La méthode et les sources
de l’inspiration Diablo sont dans [`REFERENCE-Diablo.md`](REFERENCE-Diablo.md).

## Trente cartes réellement générées

Dix nouvelles sauvegardes ont chacune chargé les trois étages. L’observateur
en lecture seule exporte les couches vivantes, le collisionneur et les unités
réellement créées. Les budgets ci-dessous ne sont pas de simples demandes
d’apparition lues dans les fichiers de groupes.

| Étage | Secteurs occupés observés | Ennemis apparus | XP de base totale disponible |
| --- | ---: | ---: | ---: |
| 1 | 26–33 | 157–208 | 314–416 |
| 2 | 29–35 | 168–218 | 672–872 |
| 3 | 27–35 | 174–212 | 1 392–1 696 |

Les trente terrains ont des géométries distinctes. Les chemins vers les clés et
la sortie sont accessibles, et les 51 portes obligatoires observées restent
non contournables. Tous les ennemis exportés sont accessibles après ouverture
des mécanismes locaux. Les populations effectives restent dans les intervalles
demandés ; aucune apparition incomplète n’est signalée dans les journaux finaux.
Les cartes possèdent entre une et sept liaisons supplémentaires sauvegardées.

Les trente parcours principaux satisfont leur minimum ; aucun ne termine sur
le plafond des 200 000 tentatives. Le maximum observé est de 39 283 tentatives.
Cet échantillon ne démontre pas une garantie absolue pour toutes les graines :
le moteur conserve un plafond fini et la QA contrôle le résultat réel.

Dans les dix séries, additionner l’XP de base des ennemis effectivement apparus
permet de finir les trois étages aux niveaux **2, 3 puis 4**. Les seuils cumulés
sont 256, 768 et 1 792 XP. Au premier étage, 128 ennemis suffisent au niveau 2,
soit environ 62 à 82 % des populations observées. Ces projections supposent la
défaite des ennemis concernés, sans bonus d’équipement ni partage de groupe.
Elles ne constituent pas dix parties de combat jouées manuellement.

Une chapelle intérieure et une chambre forte à deux mécanismes ont aussi été
testées par clic. La récompense reste inaccessible avant l’ouverture ; le
premier sceau ne suffit pas à ouvrir la chambre forte. Les ouvertures, les
couches du terrain et les liaisons restent identiques après rechargement.

Résultats complets : [`large-floors-native-results.json`](large-floors-native-results.json)
et [`large-floors-native-checks.json`](large-floors-native-checks.json).

## Corrections produites par les essais

La première série a révélé deux épuisements du plafond de 5 000 tentatives,
dont une carte réduite à 12 secteurs. Les observations sont conservées dans
[`large-floors-first-pass.json`](large-floors-first-pass.json). Le budget de
tentatives a été augmenté et les assertions sur la taille réelle renforcées.

Le contrôle des unités a ensuite trouvé un zombie enfermé dans une cellule
devenue solide après un raccord ajouté. Copier toute la bande latérale native
refermait du terrain après les apparitions. Les raccords ne modifient maintenant
que les cellules à ouvrir, et la capacité des zones d’apparition reste valide
avec les différentes sorties natives. Détail conservé dans
[`large-floors-runtime-link-finding.json`](large-floors-runtime-link-finding.json).

Ces corrections sont incluses dans les trente essais finaux. Les anciennes
observations servent à documenter les défauts trouvés, pas à valider la version.

## Contrôles statiques et moteur standard

- 23 040 combinaisons de sorties absentes, natives ou ouvertes ultérieurement.
- 5 760 contrôles de récompenses fermées non contournables ; 96 géométries de
  complexes ; 627 noms d’état vérifiés en GNU 32 et 64 bits.
- Capacité des zones après chacun des 16 masques de sorties et les trois
  variantes de raccord ; ouverture des raccords sans fermeture de terrain.
- Dimensions, palettes, absence de faces structurelles noires et 1 829
  empreintes du manifeste. Les images natives ne sont pas modifiées.
- Catégories des 139 modules et de leurs 221 groupes d’ennemis à difficulté fixe.

Rapport : [`large-floors-static-checks.json`](large-floors-static-checks.json).

L’observateur a été retiré et le moteur recompilé depuis un checkout redevenu
propre : Flare 1.15.86, révision `f9a17a266293a897a1d7eae2d54408b0de39af27`.
Un nouvel essai a validé la création native du personnage, le clic sur l’entrée
du hameau, le chargement des trois ambiances et le retour dans le même hameau.
Les étages profonds ont été atteints par la console dans cet essai de compatibilité.
Aucun moteur modifié n’est nécessaire pour jouer au mod distribué.

Les observations ont été conservées avant suppression des sauvegardes jetables.
Les journaux gardent les diagnostics déjà connus sur certaines quantités nulles
d’objets et l’image de menu `images/menus/game_over.png` absente ; ce travail
ne les corrige pas.

## Portée et reproduction

La génération conserve la grille native de secteurs et les variantes de salles
calculées par l’outil. Elle n’est pas une géométrie entièrement libre à l’échelle
de tout l’étage. Le mod compte trois étages ; les vingt étages et leurs boss
restent à intégrer. La durée d’exploration, le butin et la difficulté ressentie
des combats demandent encore des essais de jeu complets.

Une nouvelle partie est nécessaire pour tester ces cartes : les anciennes
sauvegardes conservent leurs cartes générées.

```sh
python3 -B tools/check_exploration.py
python3 -B tools/check_population.py
python3 -B tools/check_themes.py
python3 -B tools/check_encounters.py
```

Les outils `qa_themes_native.py --runs 10` et `qa_themes_stock.py` reproduisent
les campagnes natives dans un laboratoire équipé, avec `--lab` et
`--engine-repo`. Les précisions de reconstruction et de reprise sont dans
[`REPRISE-grands-etages.md`](REPRISE-grands-etages.md).
