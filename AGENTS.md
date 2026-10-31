# Règles de travail de Diantre

- Travailler directement sur `main`. Ne pas créer de branche ou de pull request
  sans demande explicite de l’utilisateur.
- Faire des commits et des pushes réguliers pendant le travail, sans attendre
  une demande ou la fin des tests : à chaque étape cohérente et au plus tard
  après dix minutes de modifications non publiées.
- Sauvegarder le travail avant une longue compilation, une campagne de tests
  ou une interruption. Un commit intermédiaire doit préciser les validations
  encore en cours ; il ne doit pas prétendre que la version est terminée.
- Le cœur du mod est la qualité de la génération procédurale. Chaque essai
  doit vérifier un comportement ou résoudre un défaut précis et consigner les
  observations utiles avant de supprimer les sauvegardes de test.
- Utiliser des sauvegardes de test séparées de celles du joueur. Créer une
  nouvelle partie entre les séries de génération.
- Garder les graphismes natifs et un mod jouable avec le moteur Flare standard.
- La difficulté des ennemis hostiles dépend de l’étage, jamais du niveau ou des
  caractéristiques du héros. Prévoir un boss aux étages 5, 10, 15 et 20.
  Utiliser la campagne Empyrean comme référence de progression ; distinguer les
  candidats de conception des rencontres effectivement intégrées et testées.
- Communiquer en français. Donner le commit publié et les limites concrètes
  des vérifications effectuées.
