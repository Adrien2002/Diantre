# Validation de Diantre 0.6.0 — en cours

Les outils et les données restaurés sont sauvegardés progressivement sur
`main`. Ce document sera complété avec les nouveaux essais dans Flare avant
de déclarer la version prête à tester.

## Contrôles des données

`python3 tools/check_exploration.py` vérifie 4 320 combinaisons de sorties et de
raccords des nouveaux complexes, huit familles, 86 géométries de collision,
douze variantes de chambre forte à deux mécanismes et 72 candidats de liaison.

Les 514 noms d’états du mod sont contrôlés pour les hachages GNU 32 et 64 bits.
Le contrôle reproduit une collision effectivement observée entre deux anciens
noms de liaison d’étages différents et vérifie sa correction par les nouveaux
identifiants déterministes.

Les essais natifs de reprise, de progression et de sauvegarde sont en cours
de reconstruction après la réinitialisation du banc de test. Les données de
jeu de ce commit constituent une sauvegarde intermédiaire.

## Première série native après restauration

Six étages issus de deux sauvegardes vierges ont été exportés du moteur
Flare 1.15.86 (`f9a17a266293a897a1d7eae2d54408b0de39af27`). Les six structures
sont distinctes ; les nombres de liaisons ajoutées sont 0, 1, 1, 1, 2 et 0.
Chaque sortie est accessible après collecte des clés. Chaque porte obligatoire,
refermée indépendamment, empêche à nouveau l’accès à la sortie : aucun des six
contrôles ne trouve de contournement.

Les exports utilisent uniquement la commande d’observation en lecture seule de
`tools/qa-flare-export.patch`, appliquée au banc de test. Elle ne change ni le
terrain, ni la génération, ni les événements. Ce correctif de diagnostic ne fait
pas partie du moteur nécessaire pour jouer.

Les empreintes du terrain et les résultats détaillés sont conservés dans
`docs/native-generation-samples.json`. Les essais de rechargement et des deux
mécanismes sont encore en cours.
