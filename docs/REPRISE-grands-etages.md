# Reprise du travail — grands étages de Diantre 0.8.0

État final consigné le 31 octobre 2026. L’implémentation et sa campagne de
validation sont terminées. Le bilan détaillé et ses limites sont dans
[`VALIDATION-grands-etages.md`](VALIDATION-grands-etages.md).

## Intention et règles durables

L’utilisateur veut des étages très vastes à visiter, avec de nombreuses
rencontres réparties dans des lieux différents. La surface et l’exploration
doivent permettre la progression ; les salles ne doivent pas être remplies de
dizaines d’ennemis. Diablo est la référence demandée. Garder les caractéristiques
fixes des ennemis par profondeur, les graphismes natifs et Flare standard.
Il reste trois étages jouables. Les vingt étages et les boss tous les cinq
étages ne sont pas encore intégrés.

Travailler sur `main`, sans branche ni PR, et commit/push régulièrement pendant
le travail. Consigner les essais avant de supprimer les sauvegardes jetables.
Ne jamais utiliser les sauvegardes du joueur.

## Recherche déjà sauvegardée

- [`REFERENCE-Diablo.md`](REFERENCE-Diablo.md) contient les observations et les
  liens vers le code étudié, à une révision précise de DevilutionX.
- Référence : `diasurgical/DevilutionX`, commit
  `06d17533e6469fdafaac724bcb36c4b69b71a273`.
- `Source/levels/drlg_l1.cpp` : chambres puis pièces adjacentes ; emprise
  minimale de 533, 693, puis 761 cases de structure selon l’étage de cathédrale.
- `Source/monster.cpp`, `InitMonsters` : population supplémentaire calculée
  depuis les cases non solides (`na / 30`), avec plafonds et exceptions.
  `PlaceGroup` répartit de petits groupes dans des positions autorisées.
- Il s’agit de principes adaptés à Flare ; aucune équivalence directe entre
  tailles de cases ou statistiques des deux jeux n’est revendiquée. Aucun code
  ni graphisme de Diablo n’est repris.

## Changements déjà publiés

Le dernier commit de données de jeu est
`6f67ee5d969e64184c009c167dc4120765638414`.

- Version 0.8.0, région de 216 × 216 cases, grille 6 × 6, carte carrée de
  232 × 232 avec marge. Emprise de génération multipliée par 2,25.
- Parcours principal configuré entre 26 et 30 secteurs ; branches de 4 à 6
  configurées, trois racines de branche au maximum par palier de porte.
  Attention : le moteur 1.15.86 utilise `min(branch_length_min, branch_length_max)`
  comme borne haute de son tirage ; dans cette configuration, les branches
  tentent donc quatre pas. La diversité vient aussi de leur position et des
  liaisons supplémentaires. Ne pas annoncer des longueurs tirées de quatre à six.
- Deux zones de 7 × 7 par secteur ordinaire, chacune avec trois à quatre
  ennemis. Leurs centres sont distants d’au moins 18 cases.
- Capacité des zones vérifiée pour les 16 masques de sorties et les trois
  variantes de raccord. Les 96 complexes et les trois ambiances sont conservés.
- XP inchangées : 2, 4 et 8 par ennemi selon les trois étages. Seuils cumulés
  de niveau 2/3/4 : 256/768/1792. Le budget minimal théorique est de 130 ennemis
  par étage, sous les hypothèses explicites du contrôleur de population.
- Les raccords ajoutés dans le jeu ne modifient désormais que les cellules à
  ouvrir. Ils ne referment plus des cellules où un ennemi a pu apparaître.

La grille de secteurs reste présente. Ce travail n’est pas un générateur de
géométrie entièrement libre sur tout l’étage, ni un équilibrage de combat final.

## Défauts réellement trouvés pendant les essais

1. Le plafond de 5 000 tentatives du générateur natif a été atteint deux fois
   sur neuf cartes. Une carte a fini avec 12 secteurs et 69 ennemis. Le plafond
   est porté à 200 000 ; la QA rejette maintenant les chemins natifs trop courts,
   les générations épuisant leurs tentatives et les populations insuffisantes.
   Observations : [`large-floors-first-pass.json`](large-floors-first-pass.json).
2. Un zombie réellement exporté à (104.5, 129.5) occupait une cellule devenue
   solide après un raccord ajouté. Le remplacement de toute la bande latérale
   fermait une partie du terrain après l’apparition des unités. Les raccords
   ouvrent maintenant uniquement leurs passages. Détail :
   [`large-floors-runtime-link-finding.json`](large-floors-runtime-link-finding.json).

## Vérifications terminées

Les résultats statiques récents sont dans
[`large-floors-static-checks.json`](large-floors-static-checks.json) :

- 23 040 configurations mêlant côtés absents, raccords natifs et ouvertures
  ultérieures ; 5 760 contrôles de chambres fermées non contournables.
- 96 géométries différentes ; 627 noms d’état sans collision GNU 32/64 bits.
- Palettes, dimensions, 1 829 empreintes, capacité des apparitions et XP fixes.

Le contrôle de population native utilise les unités réellement créées, et non
seulement les nombres demandés dans les groupes. Il vérifie leur accessibilité
après ouverture des mécanismes locaux. Les niveaux de personnage projetés sont
des calculs sur l’XP disponible après nettoyage ; ce ne sont pas des parties
de combat jouées manuellement.

## Validation terminée et commandes de reproduction

La campagne de dix sauvegardes fraîches, trois étages chacune, est terminée sur
les données corrigées : trente géométries distinctes, 51 portes obligatoires
non contournables, 157 à 218 ennemis effectivement apparus par étage. Les dix
séries disposent de l’XP de base nécessaire aux niveaux 2, 3 puis 4 après
nettoyage. La chapelle et la chambre à deux sceaux passent leurs essais de clic
et rechargement. Aucun chemin trop court ni ennemi inaccessible ne subsiste
dans cet échantillon. Le moteur a ensuite été remis à son état d’origine et
recompilé : le nouvel essai sans observateur valide la création du personnage,
l’entrée du hameau, les trois ambiances et le retour au même hameau. Résultats
détaillés : `large-floors-native-results.json` et
`large-floors-native-checks.json`.

```sh
python3 -B tools/qa_themes_native.py --lab ../diantre-expanse-lab --engine-repo ../flare-engine --runs 10
```

Le moteur de laboratoire utilise `tools/qa-flare-export.patch`, un observateur
en lecture seule des couches, du collisionneur et des unités. Les résultats
sont écrits progressivement dans `native-<horodatage>/native-results.json` ; le
bilan final est dans `native-report.json`. Examiner aussi les journaux pour les
tentatives épuisées et les apparitions incomplètes. Les sauvegardes temporaires
sont supprimées après consignation ; les observations et copies de caches sont
conservées. Le journal de la campagne courante est
`../diantre-expanse-lab/native-session-complete.log`.

État à conserver pour la suite :

- Les trente populations, tailles, XP, niveaux projetés, chemins et deux
  interactions ciblées ont été vérifiés. Ne pas les refaire sans modification
  ou nouveau problème justifiant une nouvelle série.
- Le moteur de laboratoire est revenu au code standard, propre dans Git, puis
  recompilé. L’observateur doit être réappliqué pour une nouvelle campagne
  d’exports ; il ne fait pas partie du moteur distribué.
- Le plan complet `Diantre-0.8.0-etage-entier.png` est déjà créé et enregistré
  durablement (identifiant `libfile_335e676273688191916d2e5e39c503a9`). Il montre
  le premier étage réel : 31 secteurs, 188 ennemis, 376 XP.
- Les données et les outils sont publiés sur `main`. Les prochaines étapes de
  conception concernent les retours de jeu, la durée des explorations et les
  vingt étages futurs ; ne pas considérer leur équilibrage comme terminé.

## Reconstituer le laboratoire si le disque temporaire a disparu

Les données, les outils de QA, l’observateur et cette note sont sur GitHub.
Cloner `Adrien2002/Diantre` et `flareteam/flare-engine` ; la révision moteur
utilisée est `f9a17a266293a897a1d7eae2d54408b0de39af27` (1.15.86).
Le mod inclut déjà ses atlas et ressources. Lier `game/mods/default` au dossier
`mods/default` du moteur et `game/mods/diantre` au dossier du mod.

Le laboratoire de cette session est `../diantre-expanse-lab` : moteur dans
`build/flare`, dépendances Ubuntu officielles extraites dans `sysroot/usr`.
Il faut CMake, SDL2 et ses modules image/mixer/ttf, Xvfb, xdotool et xkbcomp.
Le système est Ubuntu 24.04 ; les paquets ont été résolus depuis l’instantané
officiel du 28 août 2026, vérifiés par taille et empreinte, puis extraits.
Les fichiers `package-uris.txt` et `prepare_dependencies.py` du laboratoire
permettent de refaire cette extraction tant qu’ils sont présents.

Dans cet environnement, APT ne peut pas changer d’utilisateur : sa lecture
d’index a fonctionné avec `-o APT::Sandbox::User=root` et ses répertoires d’état
et cache sous le laboratoire. Aucun secret n’est nécessaire à cette extraction.
Ne pas contourner un éventuel refus réseau ; lire les instructions de
l’environnement au début d’une reprise.

Pour CMake, employer le préfixe `sysroot/usr`, ses bibliothèques et inclusions
`x86_64-linux-gnu`, `SDL2_LIBRARY_TEMP=/lib/x86_64-linux-gnu/libSDL2-2.0.so.0`
et `-Wl,-rpath-link,<lab>/sysroot/usr/lib/x86_64-linux-gnu`. Employer des chemins
absolus pour `LD_LIBRARY_PATH`, CMake et son répertoire de construction.
Un chemin relatif de bibliothèque échoue quand CMake change de répertoire.

Les journaux précédents contiennent des diagnostics déjà connus sur des piles
d’objets de quantité nulle et `images/menus/game_over.png` absente. Les distinguer
des nouveaux défauts de génération. Les essais de la 0.7.0 restent historiques
et ne doivent pas être utilisés pour prétendre valider la 0.8.0.
