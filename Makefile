# Nocturna Calculations - Development Automation
# 
# This Makefile provides convenient commands for environment management,
# testing, development, and deployment workflows.

# Default target
.DEFAULT_GOAL := help

# Environment variables
PROJECT_NAME := nocturna-calculations
DEV_ENV := nocturna-dev
TEST_ENV := nocturna-test
PROD_ENV := nocturna-prod

# Colors for output
RESET := \033[0m
BOLD := \033[1m
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
MAGENTA := \033[35m
CYAN := \033[36m

# Helper function to print colored output
define print_header
	@echo "$(CYAN)$(BOLD)==== $1 ====$(RESET)"
endef

define print_success
	@echo "$(GREEN)✅ $1$(RESET)"
endef

define print_warning
	@echo "$(YELLOW)⚠️  $1$(RESET)"
endef

define print_error
	@echo "$(RED)❌ $1$(RESET)"
endef

##@ Help

.PHONY: help
help: ## Display this help message
	@awk 'BEGIN {FS = ":.*##"; printf "\n$(BOLD)Usage:$(RESET)\n  make $(CYAN)<target>$(RESET)\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(CYAN)%-15s$(RESET) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BOLD)%s$(RESET)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Environment Management

.PHONY: setup-dev
setup-dev: ## Setup development environment
	$(call print_header,"Setting up development environment")
	@if [ ! -f environments/development.yml ]; then \
		$(call print_error,"Development environment file not found"); \
		exit 1; \
	fi
	conda env create -f environments/development.yml --name $(DEV_ENV) || conda env update -f environments/development.yml --name $(DEV_ENV) --prune
	$(call print_success,"Development environment ready. Activate with: conda activate $(DEV_ENV)")

.PHONY: setup-test
setup-test: ## Setup testing environment
	$(call print_header,"Setting up testing environment")
	@if [ ! -f environments/testing.yml ]; then \
		$(call print_error,"Testing environment file not found"); \
		exit 1; \
	fi
	conda env create -f environments/testing.yml --name $(TEST_ENV) || conda env update -f environments/testing.yml --name $(TEST_ENV) --prune
	$(call print_success,"Testing environment ready. Activate with: conda activate $(TEST_ENV)")

.PHONY: setup-prod
setup-prod: ## Setup production environment
	$(call print_header,"Setting up production environment")
	@if [ ! -f environments/production.yml ]; then \
		$(call print_error,"Production environment file not found"); \
		exit 1; \
	fi
	conda env create -f environments/production.yml --name $(PROD_ENV) || conda env update -f environments/production.yml --name $(PROD_ENV) --prune
	$(call print_success,"Production environment ready. Activate with: conda activate $(PROD_ENV)")

.PHONY: setup-all
setup-all: setup-dev setup-test setup-prod ## Setup all environments

.PHONY: switch-env
switch-env: ## Switch environment (use ENV=dev|test|prod)
	@if [ -z "$(ENV)" ]; then \
		$(call print_warning,"Usage: make switch-env ENV=dev|test|prod"); \
		./scripts/environments/switch_environment.py --list; \
	else \
		./scripts/environments/switch_environment.py --env $(ENV); \
	fi

.PHONY: validate-env
validate-env: ## Validate current environment
	$(call print_header,"Validating environment")
	./scripts/environments/validate_environment.py

.PHONY: list-env
list-env: ## List all available environments
	./scripts/environments/switch_environment.py --list

.PHONY: clean-env
clean-env: ## Clean all project environments
	$(call print_header,"Cleaning environments")
	@echo "This will remove all Nocturna environments. Are you sure? [y/N]" && read ans && [ $${ans:-N} = y ]
	-conda env remove -n $(DEV_ENV)
	-conda env remove -n $(TEST_ENV)
	-conda env remove -n $(PROD_ENV)
	conda clean --all
	$(call print_success,"Environments cleaned")

##@ Development

.PHONY: dev-setup
dev-setup: setup-dev ## Complete development setup with database
	$(call print_header,"Running development setup")
	@echo "Make sure to activate the environment first: conda activate $(DEV_ENV)"
	@echo "Then run: python scripts/install_dev.py"

.PHONY: dev-server
dev-server: ## Start development server
	$(call print_header,"Starting development server")
	@if [ "$${CONDA_DEFAULT_ENV}" != "$(DEV_ENV)" ]; then \
		$(call print_warning,"Please activate development environment first: conda activate $(DEV_ENV)"); \
	else \
		uvicorn nocturna_calculations.api:app --reload --host 0.0.0.0 --port 8000; \
	fi

.PHONY: dev-shell
dev-shell: ## Start interactive development shell
	@if [ "$${CONDA_DEFAULT_ENV}" != "$(DEV_ENV)" ]; then \
		$(call print_warning,"Please activate development environment first: conda activate $(DEV_ENV)"); \
	else \
		ipython; \
	fi

.PHONY: jupyter
jupyter: ## Start Jupyter Lab
	@if [ "$${CONDA_DEFAULT_ENV}" != "$(DEV_ENV)" ]; then \
		$(call print_warning,"Please activate development environment first: conda activate $(DEV_ENV)"); \
	else \
		jupyter lab; \
	fi

##@ Testing

.PHONY: test
test: ## Run full test suite
	$(call print_header,"Running test suite")
	@if [ "$${CONDA_DEFAULT_ENV}" != "$(TEST_ENV)" ]; then \
		$(call print_warning,"Recommended to use testing environment: conda activate $(TEST_ENV)"); \
	fi
	./run_tests.sh

.PHONY: test-quick
test-quick: ## Run quick tests (unit tests only)
	$(call print_header,"Running quick tests")
	pytest tests/unit/ -v

.PHONY: test-unit
test-unit: ## Run unit tests
	$(call print_header,"Running unit tests")
	pytest tests/unit/ -v --cov=nocturna_calculations

.PHONY: test-integration
test-integration: ## Run integration tests
	$(call print_header,"Running integration tests")
	pytest tests/integration/ -v

.PHONY: test-api
test-api: ## Run API tests
	$(call print_header,"Running API tests")
	pytest tests/api/ -v

.PHONY: benchmark
benchmark: ## Run performance benchmarks
	$(call print_header,"Running benchmarks")
	@if [ "$${CONDA_DEFAULT_ENV}" != "$(TEST_ENV)" ]; then \
		$(call print_warning,"Recommended to use testing environment: conda activate $(TEST_ENV)"); \
	fi
	pytest tests/performance/ --benchmark-only -v

.PHONY: benchmark-save
benchmark-save: ## Save benchmark baseline
	$(call print_header,"Saving benchmark baseline")
	pytest tests/performance/ --benchmark-only --benchmark-save=baseline

.PHONY: benchmark-compare
benchmark-compare: ## Compare against benchmark baseline
	$(call print_header,"Comparing benchmarks")
	pytest tests/performance/ --benchmark-only --benchmark-compare=baseline

##@ Code Quality

.PHONY: lint
lint: ## Run code quality checks
	$(call print_header,"Running code quality checks")
	black --check .
	flake8
	isort --check-only .

.PHONY: format
format: ## Format code
	$(call print_header,"Formatting code")
	black .
	isort .
	$(call print_success,"Code formatted")

.PHONY: type-check
type-check: ## Run type checking
	$(call print_header,"Running type checks")
	mypy nocturna_calculations/

.PHONY: security
security: ## Run security checks
	$(call print_header,"Running security checks")
	bandit -r nocturna_calculations/
	safety check

.PHONY: pre-commit
pre-commit: ## Run pre-commit hooks
	$(call print_header,"Running pre-commit hooks")
	pre-commit run --all-files

.PHONY: quality
quality: lint type-check security ## Run all quality checks

##@ Database

.PHONY: db-setup
db-setup: ## Setup database
	$(call print_header,"Setting up database")
	./scripts/setup_db.sh setup

.PHONY: db-migrate
db-migrate: ## Run database migrations
	$(call print_header,"Running database migrations")
	./scripts/setup_db.sh migrate

.PHONY: db-status
db-status: ## Check database status
	./scripts/setup_db.sh status

.PHONY: db-reset
db-reset: ## Reset database
	$(call print_header,"Resetting database")
	@echo "This will destroy all data. Are you sure? [y/N]" && read ans && [ $${ans:-N} = y ]
	./scripts/setup_db.sh reset

.PHONY: db-backup
db-backup: ## Backup database
	$(call print_header,"Backing up database")
	./scripts/setup_db.sh backup

##@ Documentation

.PHONY: docs
docs: ## Build documentation
	$(call print_header,"Building documentation")
	@if [ -d "docs" ]; then \
		cd docs && make html; \
	else \
		$(call print_warning,"Documentation directory not found"); \
	fi

.PHONY: docs-serve
docs-serve: ## Serve documentation locally
	$(call print_header,"Serving documentation")
	@if [ -d "docs/_build/html" ]; then \
		cd docs/_build/html && python -m http.server 8080; \
	else \
		$(call print_warning,"Documentation not built. Run 'make docs' first"); \
	fi

##@ Maintenance

.PHONY: update-deps
update-deps: ## Update dependencies
	$(call print_header,"Updating dependencies")
	@if [ "$${CONDA_DEFAULT_ENV}" = "$(DEV_ENV)" ]; then \
		conda env update -f environments/development.yml --prune; \
	elif [ "$${CONDA_DEFAULT_ENV}" = "$(TEST_ENV)" ]; then \
		conda env update -f environments/testing.yml --prune; \
	elif [ "$${CONDA_DEFAULT_ENV}" = "$(PROD_ENV)" ]; then \
		conda env update -f environments/production.yml --prune; \
	else \
		$(call print_warning,"Please activate an environment first"); \
	fi

.PHONY: clean
clean: ## Clean build artifacts
	$(call print_header,"Cleaning build artifacts")
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	$(call print_success,"Build artifacts cleaned")

.PHONY: clean-all
clean-all: clean clean-env ## Clean everything (artifacts and environments)

.PHONY: health-check
health-check: ## Run full system health check
	$(call print_header,"Running system health check")
	@echo "Environment: $${CONDA_DEFAULT_ENV:-base}"
	@echo "Python version:"
	@python --version || $(call print_error,"Python not available")
	@echo "Conda version:"
	@conda --version || $(call print_error,"Conda not available")
	@echo "Database status:"
	@./scripts/setup_db.sh status || $(call print_warning,"Database check failed")
	@echo "Redis status:"
	@redis-cli ping || $(call print_warning,"Redis not available")
	$(call print_success,"Health check completed")

##@ CI/CD

.PHONY: ci-setup
ci-setup: ## Setup for CI/CD
	$(call print_header,"Setting up CI/CD environment")
	pip install -r requirements-test.txt

.PHONY: ci-test
ci-test: ## Run tests for CI/CD
	$(call print_header,"Running CI/CD tests")
	pytest tests/ --cov=nocturna_calculations --cov-report=xml --junitxml=junit.xml

.PHONY: ci-quality
ci-quality: ## Run quality checks for CI/CD
	$(call print_header,"Running CI/CD quality checks")
	black --check .
	flake8
	mypy nocturna_calculations/
	bandit -r nocturna_calculations/

##@ Release

.PHONY: version
version: ## Show current version
	@python -c "import nocturna_calculations; print(nocturna_calculations.__version__)" 2>/dev/null || echo "Version not available"

.PHONY: build
build: ## Build package
	$(call print_header,"Building package")
	python setup.py sdist bdist_wheel

.PHONY: install
install: ## Install package in development mode
	$(call print_header,"Installing package in development mode")
	pip install -e .

.PHONY: install-dev
install-dev: ## Install package with development dependencies
	$(call print_header,"Installing package with development dependencies")
	pip install -e ".[dev]"

# Environment validation targets
.PHONY: check-dev-env
check-dev-env:
	@if [ "$${CONDA_DEFAULT_ENV}" != "$(DEV_ENV)" ]; then \
		$(call print_error,"Development environment not active. Run: conda activate $(DEV_ENV)"); \
		exit 1; \
	fi

.PHONY: check-test-env
check-test-env:
	@if [ "$${CONDA_DEFAULT_ENV}" != "$(TEST_ENV)" ]; then \
		$(call print_error,"Testing environment not active. Run: conda activate $(TEST_ENV)"); \
		exit 1; \
	fi

# Ensure dependencies for certain targets
dev-server: check-dev-env
jupyter: check-dev-env
benchmark: check-test-env 