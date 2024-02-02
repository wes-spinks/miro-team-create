POETRY := $(shell command -v poetry 2> /dev/null)
SOURCE_FILES := app.py miro_team.py team_configs.py

.PHONY: all
all: lint unit 

.PHONY: poetry
poetry:
ifeq ($(strip $(POETRY)),)
	@python3 -m pip install --user poetry
POETRY += python3 -m poetry
endif

.PHONY: dependencies
dependencies: poetry
	@$(POETRY) config --local virtualenvs.in-project true
	@$(POETRY) install -qn --no-root

.PHONY: unit
unit: dependencies
	@$(POETRY) run pytest -v --black --junit-xml report.xml --cov-report xml:coverage.xml

.PHONY: lint 
lint: dependencies
	@echo "Sort Imports"
	-@$(POETRY) run isort --atomic --check $(SOURCE_FILES)
	@echo "Black formatting changes"
	-@$(POETRY) run black --diff $(SOURCE_FILES)|tee black-diff.txt
	@$(POETRY) run black $(SOURCE_FILES)
	@echo "Linting Issues"
	@$(POETRY) run pylint -j 0 -f msvs --exit-zero $(SOURCE_FILES)|tee lint-res.txt

requirements.txt: poetry pyproject.toml poetry.lock
	@$(POETRY) lock --no-update
	@$(POETRY) export --without-hashes -f requirements.txt --output $@

requirements-dev.txt: poetry pyproject.toml poetry.lock
	@$(POETRY) lock --no-update
	@$(POETRY) export --with dev --without-hashes -f requirements.txt --output $@

Dockerfile: requirements.txt
	@touch Dockerfile

.PHONY: docs
docs:
	-@$(POETRY) run pip install 'pdoc' > /dev/null 2>&1
	@$(POETRY) run pdoc -o public/ -d google --no-search --no-show-source $(SOURCE_FILES)

.PHONY: clean
clean:
	-@find . -name '__pycache__' -exec rm -fr {} +
	-@find . -name '*.pyc' -exec rm {} +
	-@rm .coverage black-diff.txt coverage.xml lint-res.txt report.xml 2> /dev/null || true 

.PHONY: clean-env
clean-env:
	-@rm -r .venv 2> /dev/null || true
	-@$(POETRY) env rm .venv &> /dev/null|| true
	-@rm poetry.toml 2> /dev/null || true

.PHONY: clean-all
clean-all: clean clean-env