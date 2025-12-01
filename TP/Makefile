# =========================
#        MAKEFILE
# =========================

# Commandes
PYTHON = python
PYTEST = $(PYTHON) -m pytest

# =========================
#         TESTS
# =========================

test:
	$(PYTEST)

unit_test:
	$(PYTEST) src/tests/test_triangulation.py

api_test:
	$(PYTEST) src/tests/test_api.py

perf_test:
	$(PYTEST) src/tests/test_performance.py

# =========================
#        QUALITÉ CODE
# =========================

lint:
	$(PYTHON) -m ruff check src

lint_fix:
	$(PYTHON) -m ruff check src --fix

# =========================
#        COUVERTURE
# =========================

coverage:
	$(PYTHON) -m coverage run -m pytest
	$(PYTHON) -m coverage html
	@echo "Ouvre htmlcov/index.html"

# =========================
#         DOC
# =========================

# Todo: Ajouter des commandes pour générer la documentation