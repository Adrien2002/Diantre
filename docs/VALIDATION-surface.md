# Validation de Diantre 0.5.1 — 30 octobre 2026

## Défauts visés

Les captures de test montraient des marchands masqués par la lisière, des
rangées de maisons trop éloignées, des toits contre la montagne, un sommet
rocheux dessiné au-dessus des arbres et des faces arrière noires dans le donjon.
Les anciens contrôles d’accessibilité ne vérifiaient pas ces défauts visuels.

## Contrôles des données

`python3 tools/check_surface.py` :

- 4 096 combinaisons de quartiers et d’affectations des marchands ; 64 géométries.
- Sept marchands uniques, tous accessibles depuis le point de départ.
- Accès au coffre, à l’entrée et au point de retour.
- Empreintes des maisons bloquées, toits en retrait du pied de la falaise.
- Contrôle de l’emprise projetée des sprites d’arbres devant le torse et la tête
  des marchands, en tenant compte de leur ordre de dessin.
- Périmètre fermé et aucune case praticable derrière la paroi nord.
- Seize couches de falaise dessinées avant les objets, sans plateau horizontal.

`python3 tools/check_dungeons.py` :

- 135 modules de salle, auxquels s’ajoutent neuf variantes de raccord.
- 5 571 combinaisons de sorties et de raccords vérifiées.
- 36 contrôles de portes à clé fermées, sans passage de contournement.
- Sorties inutilisées fermées ; sorties sélectionnées reliées après ouverture
  des portes locales ; coffres et leviers accessibles.
- Toutes les coordonnées d’interaction et de modification restent dans les
  limites après le passage de 48 × 48 à 36 × 36 cases.
- États distincts des salles à clé pour éviter des coffres partageant un état.

Un examen des pixels des blocs de mur employés pour les limites générées
(identifiants 136 à 151) confirme l’absence de pixels noirs opaques. Les images
natives sont inchangées ; seule leur sélection dans la définition des tuiles
change. Cela ne signifie pas que le noir du brouillard ou des zones hors carte
est supprimé.

## Essais dans Flare

Moteur 1.15.86, Linux x86-64, rendu SDL logiciel, 1280 × 720, audio désactivé.
Banc de test isolé des sauvegardes du joueur. Les déplacements par console
servent à atteindre précisément les zones à vérifier ; les interactions sont
ensuite déclenchées à la souris.

Première partie vierge :

- Examen des deux rangées de maisons, des marchands, de la lisière et de la
  paroi au nord ; aucune surface horizontale ne recouvre les arbres.
- Entrée dans l’étage 1 depuis le portail de la ville.
- Examen de l’entrée, d’une salle circulaire et de limites de salle auparavant
  dessinées avec des faces noires.
- Actionnement d’un levier de chambre forte, puis arrêt et reprise de la
  sauvegarde : le levier reste actionné.
- Ouverture d’un coffre à clé ; test d’une porte verrouillée avec une clé
  fournie par console. La clé est consommée et l’état de la porte sauvegardé.
  Ce test ne constitue pas un parcours complet de récupération du butin.
- Passages vers les étages 2 et 3 par interaction avec les escaliers, après
  placement sur une case praticable proche de chaque escalier.
- Retour depuis l’étage 3 par le script de rappel : arrivée dans la même ville.

Deuxième partie vierge, après suppression de la première sauvegarde : sept
marchands présents avec une répartition différente. Les observations utiles
sont enregistrées avant suppression des sauvegardes du banc de test.

Les trajets complets sont aussi examinés dans les cartes effectivement produites
par le moteur, en simulant la collecte des clés et l’ouverture des portes.
Cela complète les contrôles de raccords ; les milliers de combinaisons n’ont
pas été jouées une à une.

## Portée

La structure des étages reste un assemblage de modules Flare. La suppression
d’une partie de leur marge rapproche les grandes pièces ; elle ne remplace pas
le générateur par celui d’Angband. Les salles circulaires, portes, clés, leviers,
rencontres et stocks d’origine sont conservés. Les autres biomes et des énigmes
plus élaborées restent à concevoir.

Les cartes déjà générées restent celles de leur sauvegarde. Une nouvelle partie
est nécessaire pour examiner les nouvelles dispositions. Les anciens
identifiants du plateau de la ville restent définis pour lire les caches 0.5.0.

Les avertissements préexistants sur les quantités nulles de certains objets et
sur `images/menus/game_over.png` manquante restent hors de cette modification.
