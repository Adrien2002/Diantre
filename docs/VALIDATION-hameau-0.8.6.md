# Diantre 0.8.6 — correction de l'entrée et déplacement du coffre

Date : 31 octobre 2026. Statut : **publiée sur main, contrôles
statiques réussis ; rendu en jeu à confirmer.**

## Retour de jeu

L'entrée du donjon est encore visuellement amputée sur la droite,
malgré l'ancien dégagement du pied de falaise. Le coffre partagé
était dans le passage central du hameau ; il doit être près d'une
maison mais **sans suggérer que le héros y habite**.

## Entrée : cause précise et correction

Le portail natif est la tuile **228** ancrée en (12,2).
Ses paramètres dans le tileset Grassland sont :
largeur 185 pixels, décalage horizontal 89 pixels.

La colonne de falaise droite est centrée sur x=13 et repose sur
la tuile 53, largeur 170, décalage horizontal 74. En projection
isométrique, elle commence **22 pixels à droite** du portail alors
que celui-ci s'étend **96 pixels à droite** de son point d'ancrage.

La 0.8.3 avait seulement supprimé la roche du niveau 0 en x=12.
Cette intervention ne pouvait pas résoudre l'empiétement à droite.

Dans tools/build_surface.py, on supprime désormais les sprites de
falaise **cliff_00 et cliff_01 en (13,2)**. Le pied de falaise
central (12,2) reste dégagé. La roche en (13,2) demeure présente
à partir du niveau 2, au-dessus de la hauteur de l'ouverture :
aucun mur supérieur n'a été retiré. Les cases physiques de
collision, le portail 228 et son hotspot en (12,3) sont inchangés.

## Coffre partagé

Le coffre natif (sprite 76) et son interaction stash=true passent
de **(14,14)** à **(7,9)**, entre les cabanes de la partie nord.
Le coffre reste solide (collision=1) et accessible par une case
libre voisine. Il est décalé au nord de la rue y=10/11 et ne
coupe pas le chemin nord-sud x=11..13.

Ce déplacement est fait par le générateur de la carte mère,
après assemblage des quatre secteurs de ville. Il fonctionne
indépendamment des variantes ou de l'ordre des marchands et ne
transforme aucune cabane en habitation du joueur.

## Vérification

- Source : [c747f1e](https://github.com/Adrien2002/Diantre/commit/c747f1e72e3ec97e855aa74e7b5c8f4c3821c439).
- Régénération : [fa78064](https://github.com/Adrien2002/Diantre/commit/fa78064efd15fd51827484597a527c8f355845ea).
- [GitHub Actions 41241840243](https://github.com/Adrien2002/Diantre/actions/runs/41241840243) : **succès**.
- Contrôle des **4 096 assemblages** du hameau, y compris
  présence du coffre, absence du précédent coffre au carrefour,
  accès par une case voisine, proximité d'une cabane et maintien
  du passage principal.
- Vérification des deux niveaux rocheux retirés à droite,
  des niveaux 2 à 15 conservés, du portail et de ses collisions.
- Contrôles des **23 040 configurations de raccords des donjons**
  et des 1 832 empreintes de ressources également réussis.
- Inspection directe du fichier maps/town/hamlet_forest.txt régénéré :
  mapmod=object,7,9,76 et mapmod=collision,7,9,1 présents ;
  aucun hotspot stash=true en (14,14).

## Validation native à effectuer

La géométrie des sprites est vérifiée statiquement mais le rendu
final dépend du moteur isométrique et des décalages d'affichage.
Dans **une nouvelle partie**, se rendre devant la mine : vérifier
que le cadre droit de l'ouverture est entier et que l'absence de
roche ne laisse pas un trou visuellement incohérent. Inspecter
ensuite le coffre à gauche du chemin principal, près des maisons
du haut ; vérifier qu'il est visible, utilisable et qu'il ne
masque pas de marchand.

Le contenu des donjons, les portails permanents et les caractéristiques
des ennemis n'ont pas été modifiés par cette passe.
