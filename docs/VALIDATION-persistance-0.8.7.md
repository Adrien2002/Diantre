# Diantre 0.8.7 — stabilité des cartes et restauration du hameau

Date : 1er novembre 2026.

Statut : **modifications intégrées à main ; contrôle statique réussi ;
comportement de la sauvegarde et rendu graphique à confirmer en jeu.**

## Défauts observés dans les captures fournies

- Une mort, suivie d'une résurrection, a semblé déclencher une
  nouvelle génération complète du donjon : ce comportement est
  contraire au principe « une génération par personnage ».
- De retour au hameau, il ne restait plus que **trois vendeurs**.
- La porte violette ajoutée à la mine était dirigée vers
  le mauvais côté ; les retouches de falaise de la 0.8.6
  n'étaient pas la bonne correction.

## Marchands : cause établie dans le générateur

Les deux familles de secteur normal du hameau sont des modules
uniques qui contiennent chacune **deux marchands**. Leur sélection
active les états de campagne `diantre_compact_normal_a` et
`diantre_compact_normal_b`. Flare refuse de les sélectionner
une seconde fois tant que les états sont actifs. Si un cache
de carte est absent et que la génération recommence,
seuls restent les deux vendeurs du secteur `start` et
celui du secteur `end`, soit exactement **trois**.

Le générateur met maintenant dans le hameau deux événements :
`on_load` et `on_mapexit`, qui effacent uniquement ces
marqueurs techniques. Les scripts de retour et d'entrée du
donjon les effacent également, y compris en cas de retour
depuis un ancien fichier de carte.

Les marqueurs servent toujours à garantir la présence de
chaque famille lors de **l'assemblage** des secteurs :
on ne les efface qu'après la génération. Un nouveau tirage
de secours ne peut ainsi plus épuiser toutes les familles.

## Donjon : protection de la persistance

Le moteur Flare conserve les cartes procédurales dans le
dossier `saves/<save_prefix>/<slot>/maps/`, selon un nom
dérivé de l'identité de la carte. Ce dossier doit exister
**avant** le premier appel au générateur.

`maps/spawn.txt` enregistre déjà le personnage à sa création,
mais n'attendait que 1 ms avant la téléportation vers la première
carte procédurale. Ce délai a été allongé à **350 ms** pour
éviter une compétition d'ordonnancement au premier chargement.

Le script `scripts/town/enter_dungeon.txt` lance une nouvelle
sauvegarde, puis décale de **250 ms** l'entrée du premier étage.
Les identifiants de sauvegarde restent propres à Diantre
(`save_prefix=diantre`) et à chaque personnage.

Les marqueurs de sélection des variantes ordinaires du donjon
sont maintenant effacés à chaque `on_load` et `on_mapexit`
de l'étage. Ils ne sont pas des états de quête ni des clés,
et ils n'ont pas vocation à subsister au-delà du tirage initial.
Cela évite de vider progressivement les possibilités de salles
si la carte doit exceptionnellement être régénérée.

Ces protections **n'impliquent pas que les cartes sont
re-générées volontairement**. Le comportement voulu demeure
leur **réutilisation depuis le cache propre au personnage**.

## Entrée de la mine

Reprise de la falaise de la 0.8.3 : le pied central
(`cliff_00` à (12,2)) reste dégagé, mais les éléments
de droite (`cliff_00`, `cliff_01` à (13,2)) sont restaurés.

Le sprite natif **228**, correspondant à la porte violette
oblique du retour de jeu, est supprimé et remplacé par la
variante native **224** de l'entrée. Le hotspot `Dungeon
Entrance` est conservé à (12,3), sans changement de collision.

L'orientation apparente du nouveau sprite reste **à confirmer
avec une nouvelle capture en jeu** : le contrôle statique
vérifie la substitution, pas la projection isométrique finale.

Le coffre partagé reste en (7,9), hors des deux rues.

## Contrôles et commits

- [22bc544](https://github.com/Adrien2002/Diantre/commit/22bc544740b5779d72571da03b950a17f879b231) :
  premier correctif de cache, marqueurs et mine.
- [097e579](https://github.com/Adrien2002/Diantre/commit/097e579950dd7eac0ef073715a45ae33bda53e95) :
  génération idempotente des événements de nettoyage.
- [5e349a3](https://github.com/Adrien2002/Diantre/commit/5e349a3e2b5f38de6dd6435e2746a195e53fc69d) :
  correction du manifeste d'actifs de démarrage.
- [f4eaeb8](https://github.com/Adrien2002/Diantre/commit/f4eaeb8a3241c178b5ea20317d7a97d181b01003) :
  données générées et publiées après validation réussie.
- [GitHub Actions 41253206193](https://github.com/Adrien2002/Diantre/actions/runs/41253206193) :
  **succès**, après deux itérations initiales bloquées par un
  manifeste d'empreintes non mis à jour.

Mesures : 23 040 configurations de raccords,
4 096 compositions du hameau, 1 832 empreintes d'actifs
et vérification des événements de persistance
`tools/check_persistence.py`.

## Test natif encore indispensable

Sur **un nouveau personnage** :

1. vérifier que le hameau comprend **sept marchands** ;
2. parcourir une partie de l'étage 1 et repérer son plan ;
3. mourir puis ressusciter et contrôler que la **topologie
   de l'étage 1 n'a pas changé** ;
4. revenir au village, s'assurer qu'il conserve la même
   géométrie et les **sept vendeurs** ;
5. quitter et relancer le jeu, puis confirmer la stabilité
   du même étage et du hameau ;
6. vérifier que l'entrée de mine est visuellement orientée
   vers le nord et que son interaction fonctionne.

Les tests statiques réussis ne remplacent pas cette séquence
en moteur. Aucun fichier de sauvegarde personnel n'a été
modifié ou effacé pour produire la 0.8.7.

**En cas de nouvel échec**, examiner le journal Flare
(`MapSaver: Could not open ...` ou `Saving map: ...`) et
la présence du fichier de carte dans le sous-dossier `maps`
de la sauvegarde. Ne pas supprimer la sauvegarde sans en
faire une copie.
