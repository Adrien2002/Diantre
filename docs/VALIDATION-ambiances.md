# Validation de Diantre 0.7.0 — en cours

Les outils et les données de trois ambiances sont sauvegardés progressivement
sur `main`. Les essais visuels dans le moteur restent en cours ; ce point de
sauvegarde ne constitue pas encore le bilan final.

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

## Portée

Le mod possède toujours trois étages et le hameau de surface. Les variantes de
pièces sont calculées par l’outil, puis assemblées par Flare ; les raccords
supplémentaires sont choisis dans le jeu et sauvegardés. La grille native
de secteurs n’est pas remplacée. Une nouvelle partie est nécessaire pour
examiner ces environnements, les anciennes cartes étant conservées en cache.
