# Validation du hameau forestier — 30 octobre 2026

## Contrôles des données

Commande : `python3 tools/check_surface.py`.

- 4 096 combinaisons de modules et d’affectations des marchands vérifiées.
- 256 géométries distinctes parmi ces combinaisons.
- Exactement sept marchands uniques dans chaque combinaison.
- Accès à chaque marchand, au coffre et à l’entrée par des cases praticables.
- Empreintes des cabanes bloquées sur toute leur profondeur.
- Aucun passage derrière le massif nord ; périmètre fermé.
- Modules carrés, dimensions de couches cohérentes et identifiants de tuiles définis.
- Sommet rocheux dessiné après les objets pour recouvrir les faces arrière noires.

Le manifeste de ressources contient 1 678 fichiers ; toutes les empreintes
SHA-256 correspondent aux fichiers présents.

## Essais dans le moteur

Flare 1.15.86, Linux x86-64, rendu SDL logiciel, affichage virtuel 1280 × 720.
Audio désactivé. Les sauvegardes utilisées sont exclusivement celles du banc
de test ; elles sont effacées entre les séries de génération.

Deux nouvelles parties sur la version finale ont produit deux répartitions
différentes avec les sept marchands. Les caches générés ont été examinés pour
distinguer un placement nouveau d’un simple rechargement de l’ancienne ville.

Sur la première partie :

1. Examen des cabanes, chemins, lisière et de l’entrée au nord.
2. Placement du personnage près de l’entrée avec la console de développement,
   puis interaction à la souris avec le portail : arrivée au premier étage.
3. Interaction à la souris avec l’escalier montant : retour au nouveau hameau.
4. Arrêt et relance du jeu avec la sauvegarde 1 : même hameau conservé.

La vérification exhaustive des trajets repose sur les données de collision et
un parcours de graphe. Les 4 096 combinaisons n’ont pas été jouées une à une.
Les positions des marchands sont vérifiées dans les cartes produites par le
moteur ; les stocks, inchangés par cette modification, n’ont pas fait l’objet
d’un nouvel audit commercial.

## Constats issus des essais et corrections

- Les premiers modules rectangulaires n’étaient copiés que partiellement par
  Flare. Ils ont été remplacés par quatre modules carrés.
- Le sommet rocheux était initialement dessiné avant les faces des falaises,
  exposant une bande noire. L’ordre des couches a été corrigé et contrôlé en jeu.
- Le massif utilise un sol rocheux naturel, et les commerces les cabanes en
  bois natives de Black Oak City. Les anciens empilements de terrasses et les
  bordures de tables/caisses ne sont pas utilisés par les nouvelles parties.

## Limites et suites

Cette version est une première déclinaison forestière à examiner visuellement.
Les autres biomes naturels seront choisis et déclinés ensuite. La disposition
reste fondée sur des modules Flare ; elle adapte les principes d’Angband sans
être une traduction exacte de son générateur.

Les murs noirs des donjons, les stocks et l’équilibrage restent des travaux
distincts. Les messages préexistants du moteur sur les objets de quantité nulle
et l’image `images/menus/game_over.png` manquante subsistent. Aucun nouveau
fichier graphique n’a été ajouté ou modifié.
