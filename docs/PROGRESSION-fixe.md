# Difficulté fixe et progression du bestiaire

## Règle retenue

La difficulté des ennemis hostiles dépend de l’étage. Le niveau et les
caractéristiques du héros ne changent ni leurs caractéristiques ni le budget
des rencontres. Revenir dans un ancien étage avec un personnage plus fort
doit donc permettre de constater sa progression.

Les familles rencontrées, leurs combinaisons et leurs positions peuvent rester
procédurales, dans une enveloppe de difficulté définie pour chaque profondeur.
Les invocations du joueur relèvent de ses compétences ; elles ne constituent
pas des ennemis hostiles à adapter à l’étage.

Un boss est prévu aux étages **5, 10, 15 et 20**. Les salles et les trajets vers
ces boss pourront varier, mais la rencontre doit être garantie. La sortie
suivante exigera sa défaite, sans accès de contournement par un raccord ajouté.
Sa défaite et sa récompense devront être enregistrées sans duplication au
rechargement. Ces rencontres ne sont pas encore intégrées : le mod possède
actuellement trois étages.

## État effectivement vérifié en 0.6.0

`python3 tools/check_encounters.py` examine les règles des cartes actives et
leurs 144 modules, soit 123 groupes d’ennemis. Leurs apparitions utilisent
`spawn_level=default` et les catégories propres à chaque étage :

| Étage | Variantes possibles | Niveau natif actuel |
| --- | ---: | --- |
| 1 | 4 | 1 |
| 2 | 6 | 2 |
| 3 | 7 | 3 |

Le contrôle résout les INCLUDE des ennemis, rejette les variantes adaptatives
du Labyrinthe de fer dans ces groupes, et refuse les apparitions dont le
niveau est remplacé ou calculé d’après le héros. Les valeurs de niveau natif
ne sont pas obligées de suivre le numéro de l’étage dans les versions futures.

Cette lecture est confirmée par le moteur Flare :

- [Map.cpp, modes d’apparition](https://github.com/flareteam/flare-engine/blob/f9a17a266293a897a1d7eae2d54408b0de39af27/src/Map.cpp) : `default` conserve le niveau natif ; les modes `hero_level` et `hero_stat` dépendent du héros. Dans un groupe de carte, les modes `source_level` et `source_stat` utilisent aussi le héros comme source.
- [EnemyGroupManager.cpp](https://github.com/flareteam/flare-engine/blob/f9a17a266293a897a1d7eae2d54408b0de39af27/src/EnemyGroupManager.cpp) : les catégories et intervalles de niveau filtrent les variantes candidates. La rareté pondère leur tirage.

Il n’était donc pas nécessaire de modifier les statistiques des trois groupes
actuels pour retirer un ajustement au héros : ils utilisaient déjà les valeurs
fixes de campagne. Le contrôle empêche une régression lors des prochains ajouts.

## Référence Empyrean

L’inventaire est extrait de [flareteam/flare-game](https://github.com/flareteam/flare-game/tree/af6eee6d339ac98011864bfe89da837fe7769c28),
révision `af6eee6d339ac98011864bfe89da837fe7769c28`.
Il contient **101 variantes de données**, de niveau natif 1 à 16, avec leurs
PV, catégories, statistiques, pouvoirs et cartes d’apparition possibles.
Ce ne sont pas 101 espèces différentes. Les variantes de groupe sont signalées.
Les variantes adaptatives `il_*` et les invocations du joueur sont exclues.

- [Catalogue lisible](bestiary/LISEZ-MOI.md)
- [Inventaire CSV](bestiary/empyrean-enemies.csv)
- [Données détaillées](bestiary/empyrean-enemies.json)

Les cartes donnent des repères concrets dans Empyrean ; elles ne garantissent
ni un ordre chronologique strict ni l’apparition de chaque candidat à chaque
partie. Les correspondances sont établies par catégories et niveaux des groupes,
ainsi que par les apparitions d’événements analysées. Les statistiques et les
fichiers sources restent consultables pour vérifier chaque proposition.

## Proposition de répartition sur vingt étages

Cette répartition est une base de conception, **pas un équilibrage testé ni
une annonce de vingt étages déjà jouables**. Les boss sont des candidats tirés
de la progression d’Empyrean.

| Profondeurs | Niveaux natifs de référence | Familles présentes dans cette plage | Candidat de boss |
| --- | --- | --- | --- |
| 1–5 | 1–4 | Gobelins, zombies, squelettes, premiers archers et mages | Seagate, niveau 4, à l’étage 5 |
| 6–10 | 5–8 | Gobelins renforcés, fourmilions, wyvernes, variantes de froid | Mez, niveau 8, à l’étage 10 |
| 11–15 | 9–12 | Minotaures, tireurs et mages renforcés, variantes de morts-vivants | Metzger, niveau 12, à l’étage 15 |
| 16–20 | 13–16 | Hobgobelins, wyvernes anciennes, variantes élémentaires avancées | Lezaith, niveau 16, à l’étage 20 |

Le numéro de profondeur ne doit pas être confondu avec un niveau de personnage.
Une espèce introduite dans une profondeur peut rester présente plus bas, avec
les mêmes caractéristiques, au milieu de groupes plus dangereux.

Les quatre repères de boss proviennent de rencontres natives existantes :

| Ennemi | Niveau | PV natifs | Carte de référence |
| --- | ---: | ---: | --- |
| Seagate | 4 | 2 160 | `st_maria_3.txt` |
| Mez | 8 | 3 760 | `temple_of_mez_3.txt` |
| Metzger | 12 | 5 040 | `wizards_tower_3.txt` |
| Lezaith | 16 | 13 280 | `the_pit.txt` |

Leur intégration demandera de reprendre les capacités, animations et dépendances
nécessaires, puis d’adapter les déclencheurs et récompenses aux règles de
Diantre. Par exemple, Mez est invulnérable dans sa carte native tant que le
mécanisme `emp_mez_trap` n’est pas activé. Copier seulement son fichier d’ennemi
ne reproduirait pas l’ensemble de cette rencontre.

Pour l’équilibrage, le niveau seul ne suffit pas : dégâts, résistances, vitesse,
portée, composition des groupes, espace de combat et budget de récompenses
doivent être examinés ensemble. L’ordre d’introduction d’Empyrean fournit les
repères ; les essais de Diantre devront régler le rythme entre ces repères.

## Reproduire l’inventaire

```sh
python3 tools/inventory_empyrean.py --game ../flare-game
python3 tools/check_encounters.py
```

La première commande lit un checkout local de Flare Game et enregistre sa
révision dans les résultats. Elle ne télécharge rien et ne modifie aucune
donnée de jeu de Diantre.
