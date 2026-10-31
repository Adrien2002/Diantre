# Diantre 0.8.5 — portails et menu natif de Flare

31 octobre 2026. Statut : **cartes générées et tests statiques réussis**,
mais expérience de jeu native 0.8.5 non encore vérifiée.

## Objectif

Portails fixes tous les **deux étages** (2, 4, 6, etc.), chacun étant
un raccourci permanent une fois découvert. Le portail ouvre un menu en
surimpression présentant uniquement les destinations débloquées. La
progression normale et les clés ne doivent jamais être contournées.

Les étages 1 à 3 sont actuellement disponibles : le premier portail
implémenté est celui de l'étage 2. Aucun portail fictif d'étage 4
n'est annoncé au joueur.

## Implantation

- Animation native : animations/npcs/return_obelisk1.txt, sans modifier
  l'image ni le moteur Flare.
- Village : PNJ à (9,14), zone déclenchante à (9,15), arrivée à
  (10,15). Placement fixe généré par tools/build_surface.py.
- Étage 2 : PNJ à (23,20), zone déclenchante à (23,21), arrivée à
  (22,21) dans le module d'entrée procédural. Ces coordonnées sont
  locales au secteur. Génération dans tools/build_exploration.py.
- Déverrouillage : état persistant **diantre_waypoint_f2**, posé
  uniquement lors de l'activation du portail de l'étage 2.
- Menus : npcs/diantre_waypoint_town.txt et
  npcs/diantre_waypoint_f2.txt. Ils utilisent les dialogues natifs
  Flare et leur filtrage de réponses par requires_status.
- Depuis le village : étage 1 toujours présent ; étage 2 affiché
  seulement si diantre_waypoint_f2 est actif.
- Depuis le portail de l'étage 2 : accès à l'étage 1, à son propre
  étage et au village, avec une commande Annuler.
- Retour au village : scripts/town/return_waypoint.txt, qui respecte
  les états de ville existants et arrive près de l'obélisque dans
  le hameau forestier.
- Les transitions d'escalier et les événements de clé ne sont pas
  modifiés. Le point de téléportation de l'étage 2 est différent
  du point stairs_up.

La structure reprend un mécanisme effectivement utilisé par Empyrean,
dans son PNJ iron_labyrinth_teleporter.txt. Le résultat est un dialogue
en surimpression, non une copie visuelle du menu Diablo II.

## Vérification

- [GitHub Actions 41234011890](https://github.com/Adrien2002/Diantre/actions/runs/41234011890) :
  exécution **réussie**.
- 23 040 raccords de modules vérifiés, 4 096 assemblages de hameau.
- 1 832 empreintes de ressources vérifiées.
- Nouveau tools/check_waypoints.py : deux terminaux, destinations,
  filtres d'états, points de sortie, points d'arrivée, espace au sol,
  animation native et déverrouillage sauvegardé.
- Nouvelle vérification dans tools/check_surface.py : accessibilité et
  dégagement de l'obélisque du village pour toutes les variantes.
- Les autres contrôles de thèmes, de combats et de population ont réussi.

Commits :

- [5bdc0b9](https://github.com/Adrien2002/Diantre/commit/5bdc0b965acb95b57a3541b1baac30453cb37f2e) :
  générateurs, dialogues, règles de déverrouillage et tests.
- [178ed69](https://github.com/Adrien2002/Diantre/commit/178ed6995997623bad0a46ab01f2cb3d50a6de0f) :
  cartes régénérées après réussite des tests.

## Limites de la campagne

Aucune nouvelle partie Flare 0.8.5 n'a été lancée pendant cette passe.
Une validation en moteur devra confirmer la lisibilité de l'animation,
l'ouverture du menu en marchant sur le portail sans répétition gênante,
les retours aux points prévus, l'absence d'étage 2 avant découverte et
sa persistance après une sauvegarde et un rechargement.

Le menu utilise l'interface native standard de Flare. Son aspect n'est
pas une reproduction pixel à pixel de Diablo II.
