# Validation de Diantre 0.7.0 — 31 octobre 2026

Les trois ambiances sont intégrées et testées dans Flare. Les données de jeu
testées sont celles du commit `41d3a2a0a546c6ff11acf4539445ba57307f9393`.
Les changements ont été publiés progressivement sur `main`.

## Différences d’environnement

- Étage 1 : ruines avec dalles fissurées, cours et colonnes.
- Étage 2 : terre et roche natives des cavernes, lobes érodés, tunnels sinueux,
  galeries minières et traces de rails dans les excavations droites.
- Étage 3 : dallages sombres du donjon natif, nefs, chapelles intérieures,
  monuments funéraires, statues et braseros animés.

Les murs des cavernes emploient le rocher entièrement texturé de l’atlas natif.
Les cryptes conservent les blocs maçonnés complets des ruines. Les images PNG
natives sont inchangées ; seules les sélections dans les palettes changent.
Les murs natifs de grotte ou de donjon dont une face est noire ne sont pas
employés seuls comme limites de pièces.

## Contrôles statiques

Les 96 complexes ont maintenant des géométries de collision distinctes. Les
tests couvrent 4 320 combinaisons de sorties et raccords, les mécanismes de
chambre forte et les douze chapelles intérieures fermées des cryptes.
Un contrôle supplémentaire vérifie que les raccords ne donnent pas accès aux
récompenses tant que leurs portes sont fermées.

Les palettes de chaque étage sont vérifiées avec les modules qui les utilisent.
Les limites maçonnées, les rochers de limite et les surfaces supérieures retenus
ne contiennent aucun pixel noir opaque. Les cases de structure possèdent aussi
un sol sous leurs objets, afin de ne pas montrer de vide entre les sprites.

Les niveaux fixes des ennemis et les exigences de progression sont conservés.
Les contrôles des états restent actifs, notamment le test des collisions de
leurs hachages GNU 32 et 64 bits.

Résultats détaillés : [`themes-static-checks.json`](themes-static-checks.json).
Le contrôle couvre aussi les 1 829 empreintes du manifeste et les 139 modules
actifs, dont 118 groupes d’ennemis à difficulté fixe.

## Essais dans Flare

Trois nouvelles sauvegardes de test ont chacune généré les trois étages : neuf
cartes fraîches, avec neuf géométries de collision différentes. Les couches
vivantes et le collisionneur du moteur ont été exportés par un observateur en
lecture seule. Les neuf cartes passent les contrôles d’accès aux clés et à la
sortie ; leurs neuf portes obligatoires ne peuvent pas être contournées.
Les palettes chargées correspondent à leur étage. Le nombre de boucles
supplémentaires observé varie entre zéro et deux selon la carte.

Une chapelle des cryptes a été testée par clic : coffre inaccessible avant
l’ouverture, accessible après, état et terrain identiques après sauvegarde et
rechargement. Une chambre forte des cavernes a aussi été testée par clic : le
premier mécanisme laisse la grille fermée, le second l’ouvre, puis le
rechargement conserve cet état. Ce sont deux essais d’interaction ciblés ; les
autres variantes sont couvertes par les contrôles statiques.

L’inspection visuelle a également révélé un mauvais assemblage des grilles :
leurs deux éléments étaient espacés ou orientés dans l’autre axe. Les portes
ordinaires utilisent maintenant deux cellules adjacentes avec les bons
éléments horizontaux ; les grilles de chambre forte utilisent les éléments
verticaux. Les essais et captures finaux portent sur cet assemblage corrigé.

Les captures rapprochées viennent des cartes générées. Les vues d’ensemble
montrent trois modules livrés, chargés isolément pour rendre leur architecture
visible ; leur fond noir extérieur ne représente pas une face de mur manquante.
Les textures natives ne sont pas retouchées.

L’observateur a ensuite été retiré, le moteur remis à son état Git d’origine et
recompilé. Un nouvel essai avec ce moteur standard a validé la création du
personnage, le clic sur l’entrée du hameau, le chargement des trois palettes et
le retour dans le même hameau. Les étages profonds ont été atteints par la
console pendant cet essai de compatibilité ; il ne constitue pas une partie
complète jouée manuellement.

Références utilisées : moteur Flare 1.15.86 au commit
`f9a17a266293a897a1d7eae2d54408b0de39af27`, ressources Flare Game au commit
`af6eee6d339ac98011864bfe89da837fe7769c28`.

Résultats : [`themes-native-checks.json`](themes-native-checks.json) et
[`themes-native-results.json`](themes-native-results.json).
Les observations ont été enregistrées avant de supprimer les sauvegardes
jetables ; aucune sauvegarde du joueur n’a été utilisée.

Pour reproduire les essais dans un laboratoire équipé de Flare, Xvfb et
xdotool, utiliser `tools/qa_themes_native.py` avec l’observateur
`tools/qa-flare-export.patch`, puis retirer l’observateur, recompiler et lancer
`tools/qa_themes_stock.py`. Les deux outils acceptent `--lab` et `--engine-repo`.

Les journaux ne sont pas exempts d’avertissements : ils signalent notamment
des piles d’objets de quantité nulle (753, 2000, 2001, 2002) et l’image de menu
`images/menus/game_over.png` absente. Ces diagnostics ne sont pas corrigés par
ce travail sur les ambiances. Les absences initiales de caches de brouillard
concernent les sauvegardes de test neuves.

## Portée

Le mod possède toujours trois étages et le hameau de surface. Les variantes de
pièces sont calculées par l’outil, puis assemblées par Flare ; les raccords
supplémentaires sont choisis dans le jeu et sauvegardés. La grille native
de secteurs n’est pas remplacée. Une nouvelle partie est nécessaire pour
examiner ces environnements, les anciennes cartes étant conservées en cache.
