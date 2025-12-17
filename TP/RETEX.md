# Retour d'Expérience (RETEX) - Projet de Tests & Triangulation
## Bilan Global
Mon ressenti général sur ce projet est très positif. Ce fut une excellente expérience d'apprentissage qui m'a permis de consolider de nombreuses compétences techniques. J'ai particulièrement apprécié le cadre de travail : la répartition horaire était bien équilibrée, permettant d'avancer sans pression excessive, et l'accompagnement pédagogique (professeur concis et agréable) a grandement facilité la progression.

## Analyse de la Démarche et du Plan Initial
### Ce qui a bien fonctionné
Je pense m'être bien débrouillé dans l'ensemble. L'un des points forts a été ma capacité à persévérer malgré un démarrage incertain.

Concernant mon plan de test initial, je le qualifierais de bon avec le recul. Même si ma vision était "floue" au moment de sa rédaction et que je n'étais pas certain de la direction à prendre, ce plan a finalement rempli son rôle : il m'a servi de guide pour identifier les éléments critiques à tester. Il s'est avéré que le travail produit dès le début était de qualité, ce qui a été une agréable surprise lors de l'assemblage final.

### Ce qui était moins bien / Ce qui a manqué
Le principal point de friction a été ce sentiment de flou au démarrage. J'ai avancé un peu à l'aveugle au début, doutant de la pertinence de mon premier plan, alors qu'il était finalement correct.

Sur le plan technique, j'ai constaté une dégradation importante des performances lors de tests sur de grands volumes de données. Je me suis arrêté à un seuil de **2 000 points** pour les tests de performance afin de rester dans des temps raisonnables. Lors de mes essais à **10 000 points**, l'exécution prenait environ **2 minutes**. 

Cette lenteur s'explique par deux facteurs principaux :
1. **Complexité algorithmique** : L'implémentation actuelle de l'algorithme de Bowyer-Watson a une complexité théorique de $O(n^2)$ dans le pire des cas, ce qui entraîne une explosion du temps de calcul dès que le nombre de points devient grand.
2. **Implémentation Python pur** : Le traitement de boucles imbriquées pour vérifier les cercles circonscrits sur des milliers de points est coûteux sans l'utilisation de bibliothèques optimisées (comme NumPy), qui n'étaient pas autorisées ici.

### Critique de la Stratégie de Test
J'estime avoir très bien réalisé la partie purement liée aux tests. Ma suite de tests couvre l'essentiel des fonctionnalités et garantit la robustesse de l'application :

- Tests unitaires.

- Tests de l'API (codes de retour HTTP).

- Tests de performance.

**Pistes d'amélioration** : 
- **Cas de tests contrôlés** : Avec plus de temps, j'aurais souhaité ajouter des cas de tests "faits main" avec des coordonnées fixes et des résultats attendus pré-calculés géométriquement. Cela permettrait de valider la topologie exacte de la triangulation, plutôt que de se reposer principalement sur des nuages de points aléatoires.
- **Cas limites** : J'aurais également pu ajouter davantage de configurations de points très exotiques (points presque alignés ou très proches) pour pousser l'algorithme dans ses retranchements géométriques.

## Conclusion et Recul
Avec le recul, je ne pense pas que je ferais les choses différemment. L'enchaînement des étapes s'est fait naturellement et la dynamique de travail était fluide.

Ce projet m'a prouvé que même avec une vision initiale légèrement floue, le fait de suivre une méthodologie de test rigoureuse permet d'aboutir à un résultat solide et fonctionnel.


