# Makefile pour le projet Triangulator

# Variables pour garantir l'utilisation des bons exécutables
PYTHON := python
PYTEST = $(PYTHON) -m pytest
COVERAGE = $(PYTHON) -m coverage
RUFF = $(PYTHON) -m ruff
PDOC = $(PYTHON) -m pdoc

# Ajout du répertoire courant au PYTHONPATH pour que 'src' soit trouvé
export PYTHONPATH := .

.PHONY: test unit_test perf_test coverage lint doc clean

# 1. Lance tous les tests
test:
	$(PYTEST) -v

# 2. Lance tous les tests sauf ceux de performance (marqués 'perf')
unit_test:
	$(PYTEST) -v -m "not perf"

# 3. Lance uniquement les tests de performance
perf_test:
	$(PYTEST) -v -m "perf"

# 4. Génère un rapport de couverture de code
coverage:
	$(COVERAGE) run -m pytest
	$(COVERAGE) report -m
	@echo "Rapport HTML généré dans htmlcov/"
	$(COVERAGE) html

# 5. Valide la qualité du code avec ruff
lint:
	$(RUFF) check .

# 6. Génère la documentation en HTML
doc:
	$(PDOC) --html --output-dir docs --force src/triangulator
	@echo "Documentation générée dans docs/"

# Nettoyage des fichiers temporaires (optionnel mais pratique)
clean:
	rm -rf .pytest_cache
	rm -rf __pycache__
	rm -rf htmlcov
	rm -rf docs
	rm -f .coverage