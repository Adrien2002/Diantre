# Validation de Diantre 0.6.0 — 31 octobre 2026

## Comportement livré

Les secteurs ordinaires contiennent désormais des ensembles de pièces :
chambres jointives, galeries, embranchements et circuits autour de massifs.
Huit familles fournissent 96 variantes sur les trois étages. La grille native
assemble ces ensembles ; des raccords supplémentaires sont ensuite choisis
par les événements de Flare entre secteurs du même palier de progression.
Une liaison est choisie lorsqu’au moins un raccord sûr existe, puis d’autres
peuvent être ajoutés. Les choix restent enregistrés pour la carte.

Une chambre forte facultative exige deux mécanismes dans des pièces distinctes.
Elle ne contient aucune clé ou sortie nécessaire à la progression. Chaque
variante possède ses propres états de mécanismes, de porte et de coffre.

## Contrôles des données

`python3 tools/check_exploration.py` passe :

- 4 320 combinaisons de sorties et de raccords des nouveaux complexes.
- Huit familles, 86 géométries de collision distinctes parmi les 96 variantes.
- Douze variantes de chambre forte : mécanismes accessibles avant ouverture,
  récompense inaccessible avec un seul mécanisme et accessible avec les deux.
- 72 candidats de liaison : mêmes paliers, sorties inutilisées, raccords des
  deux côtés appliqués ensemble, hors de la chambre forte.
- 514 noms d’états contrôlés avec les hachages GNU 32 et 64 bits.

Les 514 hachages 64 bits sont également comparés à ceux de
`std::collate<char>::hash` dans un programme C++ natif. Le contrôle reproduit
une collision réellement découverte entre les anciens noms
`diantre_f1_loop_1_1_south` et `diantre_f3_loop_1_0_south`. Les nouveaux noms
portent un préfixe déterministe et passent les contrôles de collision.

Les 1 832 empreintes du manifeste correspondent aux fichiers. Les tuiles des
144 modules d’exploration sont définies. Le pixel natif utilisé pour les
marqueurs est transparent. Une seconde génération des données produit les
mêmes fichiers ; aucune image native n’a été modifiée.

## Essais dans le moteur

Flare 1.15.86, source `f9a17a266293a897a1d7eae2d54408b0de39af27`, Linux x86-64,
SDL sous Xvfb, 1 280 × 720, audio désactivé. Les sauvegardes du banc sont
séparées de celles du joueur. Les déplacements par console servent à atteindre
les interactions à vérifier ; les mécanismes sont actionnés à la souris.

Les douze étages retenus proviennent de quatre séries vierges, trois étages
par série. Les douze terrains ont des empreintes distinctes. Les nombres de
liaisons ajoutées sont 0, 1, 1, 1, 2, 0, 1, 1, 1, 1, 1 et 2. Les deux étages
sans liaison supplémentaire ne présentent aucun raccord sûr disponible.

Pour chacun des douze étages, le contrôle du terrain réellement chargé vérifie
les raccords ajoutés et simule la collecte des clés et l’ouverture des portes
locales. La sortie devient accessible. Chaque porte obligatoire est ensuite
refermée indépendamment : la sortie devient inaccessible. Les douze contrôles
ne trouvent aucun contournement.

Les exports emploient la commande d’observation en lecture seule de
`tools/qa-flare-export.patch`. Elle ne change ni la génération, ni le terrain,
ni les événements. Les valeurs temporaires de collision 7 et 8 représentant
les occupants sont normalisées avant la comparaison des terrains.

L’échantillon final comprend les séries 1, 2, 3 et 5. La série 4 réutilisait deux
cartes en cache ; elle est exclue des générations neuves. La série de remplacement
utilise un nouveau répertoire de données, vide avant le lancement du moteur.
Les empreintes et résultats sont dans `docs/native-generation-samples.json`.

### Interactions et rechargement

- Reprise d’un étage : même empreinte de terrain, mêmes liaisons choisies.
- Mécanisme A seul : la chambre forte reste fermée ; A puis B : elle s’ouvre.
- Dans une copie native vierge de la chambre forte, B seul : elle reste fermée ;
  B puis A : elle s’ouvre.
- Après arrêt et reprise : les deux mécanismes et l’ouverture sont conservés ;
  les couches graphiques, le terrain et les liaisons restent identiques.

### Moteur standard

Le correctif d’observation est retiré, la source du moteur est vérifiée propre
et le moteur est recompilé avant un dernier essai avec un nouveau personnage :

- Sept marchands présents dans le hameau généré.
- Entrée dans l’étage 1 par interaction avec le portail du village.
- Initialisation des états et des nouveaux raccords terminée et sauvegardée.
- Rappel vers le même village ; empreinte de son cache inchangée.

Ce dernier essai fonctionne avec le moteur standard. Aucun moteur modifié ni
Python n’est nécessaire pour jouer. Le bilan structuré est conservé dans
`docs/generation-validation-results.json`.

## Portée et suite

Cette version change les espaces et les parcours, mais utilise encore la
grille de secteurs native de Flare. Les variantes sont produites par l’outil
Python, puis assemblées dans le jeu ; les liaisons supplémentaires sont tirées
pendant la partie. Ce n’est pas un placement arbitraire de salles comme celui
d’un générateur complet d’Angband. Le nombre de variantes ne suffit pas à
établir la qualité ressentie : rythme des découvertes, identité des lieux et
répétitions restent à évaluer en jouant.

Les essais ne constituent pas douze parcours de combat complets. Les
avertissements préexistants sur certaines quantités d’objets et sur l’image
`images/menus/game_over.png` manquante restent hors de cette modification.

Créer une nouvelle partie avec Flare 1.15 ou ultérieur pour tester la nouvelle
génération. Les cartes déjà produites restent dans leurs sauvegardes.
Les observations et résultats sont enregistrés avant suppression des
sauvegardes temporaires du banc.
