# Plan de Tests

## Portée du test
__Composant testé__ : Triangulator

__Composant simulé__ : PointSetManager ( Mock )

## 1. Les tests unitaires

__Encodage / Décodage binaire__ :

- vérification des regle de la conversion entre points et binaire
- cas testé n=1, n=5, tailles incohérente, non définies, immense, etc ..

__Triangulation__:

- cas basique de 3 points non colinéaire -> 1 triangle
- cas de 4 points convexe -> 2 triangle qui partagent leur diagonales
- cas de points uniquement colinéaires -> 0 triangle ou erreur
- cas de 2 points -> erreur
- cas de plusieurs points non colinéaire -> x triangles
- cas de plusieurs point colinéaire et non colinéaire -> y triangles

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