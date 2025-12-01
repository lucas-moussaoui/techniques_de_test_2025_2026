# Plan de Tests

## Portée du test
__Composant testé__ : Triangulator

__Composant simulé__ : PointSetManager ( Mock )

## Objectifs de validation

- la logique de triangulation fonctionne correctement
- la logique d'encodage et décodage binaire fonctionne correctement (PointSet et Triangle)
- le service HTTP répond correctement aux différentes situations (succès, erreurs client, erreurs serveur)
- la séparation claire entre tests unitaires, tests d'API, tests de performance et tests de qualité

## 1. Les tests unitaires

### Encodage / Décodage binaire

Objectif : vérifier que les formats binaires `PointSet` et `Triangles` respectent les règles définies.

Cas testés :
- Encodage d’un PointSet valide (n = 3).
- Encodage d’un PointSet vide.
- Décodage correct d’un PointSet.
- Décodage d’un PointSet invalide.
- Encodage de triangles (avec ou sans triangles).
- Décodage correct des triangles.
- Décodage de triangles invalides (erreur attendue).

Ces tests couvrent :
- données valides,
- données vides,
- données incohérentes,
- erreurs de format.
- 
### Triangulation

Objectif : valider la logique de triangulation sur différents ensembles de points.

Cas testés :
- 3 points non colinéaires → 1 triangle.
- 4 points convexes → 2 triangles.
- Points colinéaires → erreur.
- Seulement 2 points → erreur.
- Plusieurs points non colinéaires → ≥1 triangle.
- Points colinéaires + points non colinéaires → triangles valides.
- Aucun point → aucun triangle.

### Méthode `triangulate_from_id`

### Méthode `triangulate_from_id`

Objectif : vérifier l’enchaînement des étapes internes (fetch → decode → triangulate → encode).

Cas testé :
- Succès complet : toutes les méthodes sont mockées et la valeur finale doit correspondre au retour d’`encode_triangles`.

## 2. Les tests d'API ( avec mock du PointSetManager )

| Cas | Description | Attendu |
| ------ | ------ | ------ |
| 200 OK | ID valide + PSM renvoi un PointSet correct | Réponse en binaire des triangles |
| 400 Bad Request | ID mal formé | JSON d'erreur |
| 404 Not Found | Le PSM signale un PointSetID inconnu | JSON d'erreur avec la raison |
| 500 Internal Server Error | L'algorithme de triangulation échoue | JSON d'erreur avec la raison |
| 503 Service Unvaliable | Le PSM ne répond pas | JSON d'erreur avec la raison |

Ces tests utilisent un mock HTTP du PointSetManager pour simuler toutes les réponses possibles.

## 2. Les tests de performance

Mesure du temp de calcul pour la triangulation pour :
- cas de 100 points
- cas de 1000 points
- cas de 10000 points
- cas de 10000000000000000 points ( mais je ne garanti pas d'avoir un resultat a temps (O_O) )

Objectif : rester sous un seuil de temp

## 4. Les tests de qualité

__Ruff__ (analyse statique)
- Vérifie le respect des conventions Python (PEP8, imports, docstrings).
- _Critère_ : aucun avertissement bloquant.

__Coverage__ (couverture de tests)
- Mesure la proportion de code exécutée par les tests unitaires et API.
- _Critère_ : couverture > 90 %.

__pdoc3__ (documentation automatique)
- Génère la documentation HTML à partir des docstrings.
- _Critère_ : toutes les fonctions publiques documentées.

__make__ (automatisation des commandes)
- make test → tous les tests
- make unit_test → sans performance
- make perf_test → performance uniquement
- make coverage → rapport couverture
- make lint → ruff check
- make doc → génération doc