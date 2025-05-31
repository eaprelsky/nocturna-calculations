# Nocturna Calculations - Unified Development Interface
# 
# This Makefile provides the single entry point for all project operations.
# Use 'make help' to see all available commands.

# Default target
.DEFAULT_GOAL := help

# Environment variables
PROJECT_NAME := nocturna-calculations
PYTHON := python3
BOOTSTRAP := $(PYTHON) scripts/bootstrap.py

# Active environment detection
ACTIVE_ENV := $(CONDA_DEFAULT_ENV)
ifeq ($(ACTIVE_ENV),nocturna-dev)
    ENV_TYPE := dev
else ifeq ($(ACTIVE_ENV),nocturna-test)
    ENV_TYPE := test
else ifeq ($(ACTIVE_ENV),nocturna-prod)
    ENV_TYPE := prod
else
    ENV_TYPE := none
endif

# Colors for output
RESET := \033[0m
BOLD := \033[1m
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
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
	@awk 'BEGIN {FS = ":.*##"; printf "\n$(BOLD)Usage:$(RESET)\n  make $(CYAN)<target>$(RESET)\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(CYAN)%-20s$(RESET) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BOLD)%s$(RESET)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(BOLD)Current Environment:$(RESET) $(if $(filter none,$(ENV_TYPE)),$(RED)None$(RESET),$(GREEN)$(ACTIVE_ENV)$(RESET))"

##@ Quick Start

.PHONY: setup
setup: ## Complete development setup (recommended for first time)
	$(call print_header,"Setting up development environment")
	$(BOOTSTRAP) --all
	$(call print_success,"Setup complete! Run 'conda activate nocturna-dev' to start")

.PHONY: setup-dev
setup-dev: ## Setup development environment only
	$(call print_header,"Setting up development environment")
	$(BOOTSTRAP) --env dev

.PHONY: setup-test
setup-test: ## Setup testing environment only
	$(call print_header,"Setting up testing environment")
	$(BOOTSTRAP) --env test

.PHONY: setup-prod
setup-prod: ## Setup production environment only
	$(call print_header,"Setting up production environment")
	$(BOOTSTRAP) --env prod

##@ Development

.PHONY: dev
dev: check-dev ## Start development server
	$(call print_header,"Starting development server")
	uvicorn nocturna_calculations.api:app --reload --host 0.0.0.0 --port 8000

.PHONY: shell
shell: check-dev ## Start interactive Python shell
	$(call print_header,"Starting interactive shell")
	ipython

.PHONY: jupyter
jupyter: check-dev ## Start Jupyter Lab
	$(call print_header,"Starting Jupyter Lab")
	jupyter lab

# Documentation targets - currently disabled as Sphinx is not used
# .PHONY: docs
# docs: check-dev ## Build documentation
# 	$(call print_header,"Building documentation")
# 	cd docs && make html

# .PHONY: docs-serve
# docs-serve: docs ## Serve documentation locally
# 	$(call print_header,"Serving documentation at http://localhost:8080")
# 	cd docs/_build/html && python -m http.server 8080

##@ Testing

.PHONY: test
test: check-env ## Run full test suite
	$(call print_header,"Running test suite")
	pytest tests/ -v

.PHONY: test-unit
test-unit: check-env ## Run unit tests only
	$(call print_header,"Running unit tests")
	pytest tests/unit/ -v --cov=nocturna_calculations

.PHONY: test-integration
test-integration: check-env ## Run integration tests only
	$(call print_header,"Running integration tests")
	pytest tests/integration/ -v

.PHONY: test-api
test-api: check-env ## Run API tests only
	$(call print_header,"Running API tests")
	pytest tests/api/ -v

.PHONY: coverage
coverage: check-env ## Run tests with coverage report
	$(call print_header,"Running tests with coverage")
	pytest tests/ --cov=nocturna_calculations --cov-report=html --cov-report=term

##@ Code Quality

.PHONY: format
format: check-env ## Format code with black and isort
	$(call print_header,"Formatting code")
	black .
	isort .
	$(call print_success,"Code formatted")

.PHONY: lint
lint: check-env ## Run linting checks
	$(call print_header,"Running linting checks")
	black --check .
	flake8
	isort --check-only .

.PHONY: type-check
type-check: check-env ## Run type checking with mypy
	$(call print_header,"Running type checks")
	mypy nocturna_calculations/

.PHONY: security
security: check-env ## Run security checks
	$(call print_header,"Running security checks")
	bandit -r nocturna_calculations/
	safety check

.PHONY: quality
quality: lint type-check security ## Run all code quality checks

##@ Database

.PHONY: db-setup
db-setup: ## Setup database
	$(call print_header,"Setting up database")
	./scripts/services/setup_postgres.sh setup

.PHONY: db-migrate
db-migrate: check-env ## Run database migrations
	$(call print_header,"Running database migrations")
	alembic upgrade head

.PHONY: db-reset
db-reset: ## Reset database (WARNING: destroys data)
	$(call print_header,"Resetting database")
	@echo "This will destroy all data. Are you sure? [y/N]" && read ans && [ $${ans:-N} = y ]
	./scripts/setup_db.sh reset

##@ Services

.PHONY: services-install
services-install: ## Install PostgreSQL and Redis
	$(call print_header,"Installing services")
	$(BOOTSTRAP) --install-services

.PHONY: services-start
services-start: ## Start all services
	$(call print_header,"Starting services")
	./scripts/services/setup_postgres.sh start
	./scripts/services/setup_redis.sh start

.PHONY: services-check
services-check: ## Check service status
	$(call print_header,"Checking services")
	@echo "PostgreSQL:"
	@./scripts/services/setup_postgres.sh check || true
	@echo ""
	@echo "Redis:"
	@./scripts/services/setup_redis.sh check || true

##@ Maintenance

.PHONY: clean
clean: ## Clean build artifacts and caches
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

.PHONY: update-deps
update-deps: check-env ## Update dependencies
	$(call print_header,"Updating dependencies")
	pip install --upgrade pip setuptools wheel
	pip install -e ".[$(if $(filter test,$(ENV_TYPE)),test,$(if $(filter prod,$(ENV_TYPE)),api,dev))]"
	$(call print_success,"Dependencies updated")

.PHONY: env-info
env-info: ## Show environment information
	$(call print_header,"Environment Information")
	@echo "Active Environment: $(if $(filter none,$(ENV_TYPE)),$(RED)None$(RESET),$(GREEN)$(ACTIVE_ENV)$(RESET))"
	@echo "Python Version: $$(python --version 2>&1)"
	@echo "Pip Version: $$(pip --version)"
	@echo "Project Root: $$(pwd)"
	@echo ""
	@echo "Available Environments:"
	@conda env list | grep nocturna || echo "  No Nocturna environments found"

##@ Utility Commands

.PHONY: install-hooks
install-hooks: check-dev ## Install git pre-commit hooks
	$(call print_header,"Installing pre-commit hooks")
	pre-commit install
	$(call print_success,"Pre-commit hooks installed")

.PHONY: validate
validate: quality test ## Run all validation checks

.PHONY: all
all: setup validate ## Complete setup and validation

# Internal targets

.PHONY: check-env
check-env:
	@if [ "$(ENV_TYPE)" = "none" ]; then \
		$(call print_error,"No Nocturna environment active"); \
		echo "Please activate an environment first:"; \
		echo "  conda activate nocturna-dev    # For development"; \
		echo "  conda activate nocturna-test   # For testing"; \
		echo "  conda activate nocturna-prod   # For production"; \
		exit 1; \
	fi

.PHONY: check-dev
check-dev:
	@if [ "$(ENV_TYPE)" != "dev" ]; then \
		$(call print_error,"Development environment not active"); \
		echo "Please activate: conda activate nocturna-dev"; \
		exit 1; \
	fi

# Default for common typos
.PHONY: install
install: setup ## Alias for setup

.PHONY: run
run: dev ## Alias for dev

.PHONY: serve
serve: dev ## Alias for dev 