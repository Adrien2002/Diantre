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
