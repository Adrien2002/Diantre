# Étude du procédural de Diablo I (DevilutionX) — 31 octobre 2026

Statut : **recherche sur le code source, sans changement des données de jeu de Diantre**. Ce document ne prétend ni reproduire les quatre générateurs ni démontrer un nouvel équilibrage en jeu. Il complète docs/REFERENCE-Diablo.md ; les constats de cette étude sont tirés des fonctions citées ci-dessous.

## Périmètre et références figées

- Source : diasurgical/DevilutionX, révision **06d17533e6469fdafaac724bcb36c4b69b71a273**. C'est la même révision que celle étudiée pour Diantre 0.8.0.
- Diantre : branche main, données de jeu de référence **6f67ee5d969e64184c009c167dc4120765638414** ; contrôles et passation jusqu'à **968526b677bd4c39131d90777e25fbde0c8f6fd3**.
- Les quatre environnements du **Diablo I original** sont cathédrale (1–4), catacombes (5–8), cavernes (9–12), enfer (13–16). DevilutionX gère aussi des niveaux Hellfire ; ne pas les confondre avec ceux du jeu original.
- Références de code : [gendung.cpp](https://github.com/diasurgical/DevilutionX/blob/06d17533e6469fdafaac724bcb36c4b69b71a273/Source/levels/gendung.cpp), [drlg_l1.cpp](https://github.com/diasurgical/DevilutionX/blob/06d17533e6469fdafaac724bcb36c4b69b71a273/Source/levels/drlg_l1.cpp), [drlg_l2.cpp](https://github.com/diasurgical/DevilutionX/blob/06d17533e6469fdafaac724bcb36c4b69b71a273/Source/levels/drlg_l2.cpp), [drlg_l3.cpp](https://github.com/diasurgical/DevilutionX/blob/06d17533e6469fdafaac724bcb36c4b69b71a273/Source/levels/drlg_l3.cpp), [drlg_l4.cpp](https://github.com/diasurgical/DevilutionX/blob/06d17533e6469fdafaac724bcb36c4b69b71a273/Source/levels/drlg_l4.cpp), [monster.cpp](https://github.com/diasurgical/DevilutionX/blob/06d17533e6469fdafaac724bcb36c4b69b71a273/Source/monster.cpp), [objects.cpp](https://github.com/diasurgical/DevilutionX/blob/06d17533e6469fdafaac724bcb36c4b69b71a273/Source/objects.cpp), [themes.cpp](https://github.com/diasurgical/DevilutionX/blob/06d17533e6469fdafaac724bcb36c4b69b71a273/Source/levels/themes.cpp), [diablo.cpp](https://github.com/diasurgical/DevilutionX/blob/06d17533e6469fdafaac724bcb36c4b69b71a273/Source/diablo.cpp).

## 1. Diablo n'emploie pas une méthode unique pour tous les étages

La fonction CreateDungeon dans gendung.cpp (autour des lignes 347–375) oriente la création vers CreateL5Dungeon pour la cathédrale, CreateL2Dungeon pour les catacombes, CreateL3Dungeon pour les cavernes et CreateL4Dungeon pour l'enfer. Les différences ne sont pas seulement graphiques.

### Cathédrale : volumes, extensions récursives et finitions

Dans drlg_l1.cpp :
- FirstRoom (vers 507) prépare un masque de chambres et de couloirs, avec orientation horizontale ou verticale et présence variable de chambres principales.
- GenerateRoom (vers 459) fait croître de petites pièces attenantes, en alternant les orientations et en vérifiant les limites et les occupations par CheckRoom ; il s'agit d'une construction en plusieurs étapes, pas d'une simple juxtaposition de modules identiques.
- GenerateLevel (vers 1166) rejette les propositions dont la surface du masque est inférieure à 533 cases au niveau 1, 693 au niveau 2 et 761 ensuite. Ces valeurs concernent le masque structurel de ce générateur : **ne pas les comparer directement aux cases de Flare**.
- MakeDmt, FillChambers, FixTilesPatterns, AddWall, FloodTransparencyValues, FixTransparency, FixDirtTiles, FixCornerTiles, Substitution, ApplyShadowsPatterns et FillFloor interviennent dans des passes distinctes. Un escalier doit aussi pouvoir être placé ; sinon le niveau est régénéré.
- FixCornerTiles (vers 1091) corrige explicitement des voisinages de tuiles d'angle, tandis que d'autres traitements harmonisent murs, sols et ombrages. La correction de la lecture visuelle est une étape de génération à part entière.

### Catacombes : pièces distribuées, couloirs et correction des vides

Dans drlg_l2.cpp :
- CreateRoom (vers 1771) choisit des dimensions de pièces dans un espace disponible, enregistre leurs connexions et subdivise récursivement les portions restantes. La routine limite notamment le nombre de pièces.
- ConnectHall (vers 1869) trace des liaisons entre pièces avec ajustements directionnels et préparation des portes.
- CreateDungeon (vers 2445) matérialise les passages, convertit les symboles de construction et appelle FillVoids ; un échec entraîne une nouvelle tentative.
- GenerateLevel (vers 2679) applique ensuite FixLockout, FixDoors, FixDirtTiles, une sélection abondante de minisets de portes, arches, colonnes et variations, puis Substitution et ApplyShadowsPatterns.
- **Enseignement** : la carte structurelle est suivie d'une phase de raccords et d'habillage, pas seulement d'une distribution aléatoire de tuiles.

### Cavernes : croissance irrégulière et éléments naturels

Dans drlg_l3.cpp :
- FillRoom (vers 714) et CreateBlock (vers 756) étendent récursivement des volumes de roche creusée ; des bords irréguliers sont introduits par tirage.
- GenerateLevel (vers 1988) applique plusieurs passes de correction morphologique (FillDiagonals, FillSingles, FillStraights, Edges), puis rejette un niveau dont la surface praticable est inférieure à 600 ou dont Lockout révèle un blocage.
- La création des bassins, MakeMegas, les escaliers et les éléments de quête précèdent d'autres retouches. PoolFix, River, Fence, minisets de stalactites et crevasses apportent une variété attachée au thème.
- River (vers 1014) ne consiste pas à poser indépendamment des tuiles d'eau ou de lave : la routine suit un tracé et choisit des formes de transition. PlaceLavaPool (vers 1439) emploie une recherche de zones candidates et des critères de taille.

### Enfer : agencement par quadrants et éléments imposés

Dans drlg_l4.cpp :
- FirstRoom (vers 265) construit une partie du plan ; MirrorDungeonLayout (vers 304) la réplique par symétries. **Il serait donc inexact de présenter tous les niveaux de Diablo comme dépourvus de symétries visibles**.
- GenerateLevel (vers 1145) exige une surface minimale de 692 pour ce générateur, prépare les bordures, applique les symétries et les corrections de tuiles, gère les salles de thème et certains éléments liés aux quêtes et aux profondeurs particulières.
- Le dernier environnement dispose donc de règles structurelles très différentes de celles des cavernes.

## 2. Population des monstres : budget global, puis placement local variable

Dans monster.cpp, fonction InitMonsters (vers 3690–3770) :
1. Les monstres de quêtes et uniques sont pris en compte séparément ; des zones de vision provisoires protègent les points d'arrivée.
2. La fonction compte les cases non solides d'une fenêtre de 80 × 80 cases du monde.
3. Le budget ordinaire supplémentaire est **nombre de cases non solides / 30**, avec majoration d'environ 50 % en multijoueur et plafond tenant compte des unités déjà présentes et de MaxMonsters.
4. Pour peupler ce budget, elle choisit des types disponibles et répète PlaceGroup. **Au niveau 1, les groupes ordinaires comptent toujours un individu**. Aux autres niveaux, un tirage peut encore produire un solitaire ; au niveau 2 ou en crypte, le groupe non solitaire est de **2 à 3** ; plus bas, il est de **3 à 5**. Ces branches doivent être lues avec la condition aléatoire qui choisit parfois un solitaire.
5. PlaceGroup (vers 308–380) choisit une position admissible et étend le groupe par déplacements successifs. Il contrôle les collisions, les acteurs présents, la visibilité, les setpieces et l'identité de région de transparence (dTransVal), ce qui évite de répartir artificiellement un groupe de part et d'autre d'une cloison.
6. Les groupes escortant un monstre unique ont des règles supplémentaires, notamment de maintien à proximité du chef ; ils ne sont pas équivalents aux groupes ordinaires.

**Précision :** le ratio 1/30 n'est ni un ordre de placer un ennemi toutes les trente cases, ni un budget d'XP, ni une constante universellement transposable à Flare. Il fournit un *total cible* à l'échelle du niveau, avec des restrictions et des exceptions.

## 3. Pourquoi les niveaux semblent habités : objets et salles à thème

Dans diablo.cpp, LoadGameLevelDungeon (vers 3139–3180), le jeu prépare les salles thématiques, initialise les objets, puis les monstres ordinaires, les objets au sol et enfin le contenu thématique. Il réserve certaines zones avec HoldThemeRooms et DungeonFlag::Populated pour éviter les recouvrements indésirables.

Dans objects.cpp :
- RndLocOk et IsAreaOk (vers 237–265) refusent les cases occupées, solides ou réservées. Des placements utilisent une *empreinte* de 3 × 3 ou 3 × 4 cases plutôt qu'un simple contrôle du point central.
- InitRndBarrels (vers 397) tire 3 à 7 **groupes** de tonneaux (ou d'urnes dans la crypte Hellfire) et ajoute localement des éléments voisins selon une condition d'arrêt. Il ne crée pas systématiquement des rangées de taille fixe.
- InitObjects (vers 3820+) fournit des objets propres au lieu : 10 à 14 sarcophages dans la cathédrale, tonneaux, torches et objets de quête, portes liées à la géométrie, etc. Les variantes exactes dépendent du niveau et des quêtes.

Dans themes.cpp :
- InitThemes (vers 826) choisit des identités locales, parmi notamment sanctuaire, bibliothèque, ossuaire, trésor, torture, tonneaux, fontaines, racks d'armes.
- CreateThemeRooms (vers 913) applique des règles spécifiques à chaque thème ; Theme_Barrel, Theme_SkelRoom et Theme_Treasure (vers 377–550) placent leurs éléments autrement qu'une décoration uniformément distribuée.
- PlaceThemeMonsts (vers 349) peuple certaines salles thématiques selon une fréquence par case éligible et une région dédiée. Certains éléments du thème remplacent même des objets par des squelettes.
- **Leçon** : le décor peut être narratif, spatial et fonctionnel. Une bibliothèque, un ossuaire et une salle aux tonneaux ne devraient pas être trois salles identiques avec des accessoires différents.

## 4. Comparaison avec Diantre 0.8.0 — état réellement livré

Sources Diantre : [build_exploration.py](https://github.com/Adrien2002/Diantre/blob/main/tools/build_exploration.py), [dungeon_themes.py](https://github.com/Adrien2002/Diantre/blob/main/tools/dungeon_themes.py), [check_population.py](https://github.com/Adrien2002/Diantre/blob/main/tools/check_population.py), [VALIDATION-grands-etages.md](VALIDATION-grands-etages.md).

- **Architecture** : la géométrie interne est calculée hors jeu par Complex.architecture, puis Flare assemble les complexes dans une grille 6 × 6 de secteurs de 36 × 36 cases ; des raccords s'ouvrent ensuite par scripts natifs. Les 96 variantes de complexes existent, mais ne constituent pas une géométrie libre recalculée sur tout l'étage à chaque partie.
- **Ennemis ordinaires** : encounter_groups (vers 343–370) choisit exactement deux centres par complexe ordinaire, les éloigne d'au moins 18 cases et crée deux rectangles de 7 × 7, chacun avec number=3,4. Cette décision explique la régularité « trois ou quatre ennemis » signalée en jeu ; elle ne vient pas d'une contrainte de Diablo.
- **Décoration** : add_details dans dungeon_themes.py (vers 87) place **au maximum quatre obstacles ponctuels** dans des poches de cinq cases de côté, suffisamment éloignées des éléments protégés. Quelques franges et rails spécifiques complètent ce travail. Ce traitement limité explique en partie les grands espaces perçus comme nus, sans démontrer qu'ils sont techniquement incorrects.
- **XP et progression** : les valeurs 2/4/8 XP par ennemi aux trois profondeurs sont restées intactes. Les trente cartes testées comportent 157–218 ennemis suivant l'étage, et l'XP théorique permet d'atteindre les niveaux 2/3/4 après nettoyage. Ce n'est **pas** une validation du plaisir ressenti pendant une partie.
- **Lisibilité** : des règles de collision peuvent être correctes sans que les sprites affichent des angles, piliers et murs visuellement plausibles. Les captures du joueur montrent des points à examiner ; les réparations exactes exigent d'identifier les cellules et leur assemblage, pas de poser arbitrairement des piliers.
- **Contraintes** : ne pas modifier les graphismes natifs, ne pas imposer un fork de Flare et ne pas adapter la puissance des ennemis au niveau du personnage.

## 5. Pistes d'adaptation — propositions, non implémentées

### A. Dissocier population totale et organisation des rencontres

- D'abord établir un **budget de population à l'échelle de la carte**, idéalement en lien avec le terrain **réellement praticable** et les zones protégées, puis choisir où placer les ennemis.
- Varier effectivement la granularité : solitaires, duos, trios, petits groupes, rares rassemblements plus grands ; ne plus créer systématiquement deux rectangles de 3–4 ennemis par complexe.
- Tirer les lieux dans les passages, salles, détours et espaces ouverts, pas uniquement près des centres choisis. Ne pas « placer n'importe où » au sens de traverser murs, portes verrouillées, coffres ou zones de quête.
- Préserver la difficulté fixe par profondeur ; mesurer l'XP totale sans décider immédiatement de doubler les XP individuelles.
- **Question de faisabilité à vérifier** : le moteur Flare standard peut-il tirer une densité réellement globale après assemblage, ou faut-il pré-calculer un ensemble de positions éligibles et de rencontres variables dans les modules ? Ne pas prétendre à une répartition uniforme globale tant que le fonctionnement natif n'a pas été vérifié.

### B. Faire du décor une passe structurée et thématique

- Distinguer terrain structurel, habillage de sol non bloquant, mobilier sans collision, objets interactifs et obstacles bloquants ; contrôler séparément leurs empreintes et leur lisibilité.
- Établir des **règles par environnement et par type de lieu** : maçonnerie/ruines, traces d'extraction/cavernes, monuments funéraires/cryptes.
- Réserver quelques « lieux marquants », mais peupler aussi les espaces ordinaires avec des détails sobres et irréguliers ; ne pas remplir chaque case indistinctement.
- Contrôler les accès aux clés, portes, sceaux, escaliers et coffres après chaque ajout. Le cas documenté de l'ennemi emmuré par un raccord impose de ne pas réintroduire de fermeture de terrain après apparition.

### C. Ajouter une validation de cohérence architecturale

- Contrôler les motifs de voisinage des murs, angles, ouvertures, colonnes et îlots : repérer les surfaces solides qui semblent ouvertes et les sprites « suspendus ».
- Une règle de remplacement d'angle ou de pied de mur vaut mieux qu'un pilier ajouté au hasard ; les tests doivent comparer sprite, collision et continuité du chemin.
- Distinguer les anomalies causées par la géométrie de base de celles créées à la frontière des secteurs et par les raccords en cours de chargement.

### D. Mesurer la qualité ressentie sans la réduire à un compteur

Proposer une campagne de cartes fraîches et plusieurs parties courtes, avec :
- histogramme des tailles de groupes **réellement apparus** et séparation spatiale des individus ;
- ennemis par 100 cases praticables, longueur des trajets sans rencontre et densité visible à l'échelle de la caméra de Flare ;
- distribution des objets par famille, fraction de surface sans habillage, passages bloqués, captures d'angles et de couloirs ;
- XP disponibles et XP réellement acquis au cours de la progression, temps avant premier niveau, potions consommées, durée entre combats ;
- régénération et contrôle de rechargement, maintien des clés et boss futurs non contournables ;
- tests sur Flare standard et sauvegardes **jetables séparées**.

Aucun seuil cible de densité n'est encore validé. Il devra résulter des captures et du jeu, pas d'une transposition arithmétique de Diablo.

## 6. Ordre de travail recommandé

1. **Audit visuel ciblé** des exemples fournis (angles et faux passages), inventaire des atlas et des tuiles utilisables sans retoucher les PNG.
2. **Prototype de population variable**, en préservant le total initial comme témoin ; mesurer les distributions réelles avant d'augmenter la densité.
3. **Prototype d'habillage thématique** avec collisions et accès garantis ; vérifier que les lieux ne paraissent pas clonés.
4. Ajustement du **budget global** d'ennemis et du rythme d'XP à partir de parties jouées, sans toucher à l'adaptation de niveau.
5. Validation statique + native, captures à l'échelle réelle de la caméra, puis vérification avec moteur Flare standard.

Ce document est un **résultat de lecture du code**, pas une correction des défauts du mod. Les modifications du générateur, leur compilation et leur validation restent à réaliser lors d'une étape distincte.
