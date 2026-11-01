# Diantre 0.8.8 — orientation de l'entrée dans la falaise

Date : 1er novembre 2026.

## Symptôme

Les captures du hameau montraient une ouverture qui paraît
latérale : le personnage semblait entrer dans la montagne par
le côté, au lieu d'entrer **vers le nord** depuis la prairie.

La tuile 228 de la 0.8.6, puis la tuile 224 de la 0.8.7, étaient
mal adaptées à la géométrie du mur du nord. Ce n'était ni un
problème de collisions ni une erreur de cheminement.

## Référence native vérifiée

Dans `mods/alpha_demo/maps/frontier_outpost.txt` du dépôt officiel
`flareteam/flare-game`, une entrée située **dans la rangée y=11**
est composée de deux pièces de la couche objet :

- tuile **230** en `(19,11)` ;
- tuile **231** en `(20,11)`.

Le déclencheur d'entrée occupe `(19,11,2,1)` et le chemin praticable
est du côté des y croissants (approche depuis le sud).

À l'inverse, dans `mods/empyrean_campaign/maps/perdition_harbor.txt`,
la paire 225/224 est posée verticalement en `(3,14)` et `(3,15)`,
avec un hotspot `(4,14,1,2)` sur le côté droit :
c'est une ouverture latérale.

Ces exemples établissent la distinction d'orientation indépendamment
des noms ou de la numérotation des tuiles.

## Modification

Dans `tools/build_surface.py` :

- `object,11,2,230` : moitié gauche ;
- `object,12,2,231` : moitié droite.

Le portail du hameau reste accessible depuis `(12,3)`.
Ni le relief ni les couches de collision n'ont été modifiés.
Le coffre partagé reste en `(7,9)`.

Dans `tools/check_surface.py`, de nouvelles assertions valident
les deux tuiles natives, l'absence des anciennes variantes latérales
et l'approche praticable depuis le sud.

## Résultats

- [Source et validations ce58c33](https://github.com/Adrien2002/Diantre/commit/ce58c335569ba0a9907138a4e5b59beaf2d0186a)
- [Cartes recalculées 8327ce9](https://github.com/Adrien2002/Diantre/commit/8327ce98ea4ef459e3eaba7236797fd251cce63a)
- [Workflow 41315176247](https://github.com/Adrien2002/Diantre/actions/runs/41315176247) : **réussi**.

Inspection du fichier `diantre/maps/town/hamlet_forest.txt`
régénéré : les deux `mapmod=object` attendus sont présents.

## Limite

Les tests ont vérifié les données de carte mais **pas une capture native
de Diantre 0.8.8**. La perception exacte de l'ouverture et l'éventuel
recouvrement par les sprites de falaise restent à valider en jeu.
Il est nécessaire d'utiliser une nouvelle partie, puisque Flare
peut garder la carte déjà générée dans la sauvegarde.
