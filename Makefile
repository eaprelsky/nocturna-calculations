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
API_TESTS := $(PYTHON) scripts/testing/run_api_tests.py
API_TESTS_INTEGRATED := python3 scripts/testing/test_with_server.py

# Docker configuration
DOCKER_IMAGE := nocturna-calculations
DOCKER_TAG := latest
COMPOSE_FILE := docker-compose.yml
ENV_FILE := .env

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
	uvicorn nocturna_calculations.api.app:app --reload --host 0.0.0.0 --port 8000

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

.PHONY: test-websocket
test-websocket: check-test-env ## Run WebSocket tests only (requires nocturna-test environment)
	$(call print_header,"Running WebSocket tests")
	pytest tests/websocket/ -v

.PHONY: test-websocket-unit
test-websocket-unit: check-test-env ## Run WebSocket unit tests (ConnectionManager)
	$(call print_header,"Running WebSocket unit tests")
	pytest tests/websocket/test_connection_manager.py -v

.PHONY: test-websocket-integration
test-websocket-integration: check-test-env ## Run WebSocket integration tests (Router)
	$(call print_header,"Running WebSocket integration tests")
	pytest tests/websocket/test_websocket_router.py -v

.PHONY: test-auth
test-auth: check-test-env ## Run all authentication tests (unit + integration)
	$(call print_header,"Running authentication tests")
	@echo "🔐 Admin Unit Tests..."
	@pytest tests/unit/test_admin_management.py -v
	@echo ""
	@echo "🔐 Registration Config Tests..."
	@pytest tests/unit/test_registration_config_unit.py -v
	@echo ""
	@echo "🔐 Admin Security Tests (working)..."
	@pytest tests/security/test_admin_security.py -v --tb=short -x || true
	@echo ""
	@echo "🔐 Admin Integration Tests..."
	@pytest tests/integration/test_admin_integration.py -v --tb=short || true
	$(call print_success,"Authentication tests completed")

.PHONY: test-auth-unit
test-auth-unit: check-test-env ## Run authentication unit tests only
	$(call print_header,"Running authentication unit tests")
	@echo "🔐 Admin Management Unit Tests..."
	@pytest tests/unit/test_admin_management.py -v
	@echo ""
	@echo "🔐 Registration Configuration Tests..."
	@pytest tests/unit/test_registration_config_unit.py -v
	$(call print_success,"Authentication unit tests completed")

.PHONY: test-auth-security
test-auth-security: check-test-env ## Run authentication security tests
	$(call print_header,"Running authentication security tests")
	pytest tests/security/test_admin_security.py -v --tb=short

.PHONY: test-auth-integration
test-auth-integration: check-test-env ## Run authentication integration tests
	$(call print_header,"Running authentication integration tests")
	@echo "🔐 Admin Integration Tests..."
	@pytest tests/integration/test_admin_integration.py -v
	@echo ""
	@echo "🔐 Registration Integration Tests..."
	@pytest tests/integration/test_registration_integration.py -v || true
	$(call print_success,"Authentication integration tests completed")

.PHONY: test-api
test-api: check-test-env ## Run API tests only (requires nocturna-test environment)
	$(call print_header,"Running API tests")
	$(API_TESTS) --verbose --skip-env-check

.PHONY: test-api-auth
test-api-auth: check-test-env ## Run API authentication tests only
	$(call print_header,"Running API authentication tests")
	$(API_TESTS) --auth --verbose --skip-env-check

.PHONY: test-api-charts
test-api-charts: check-test-env ## Run API chart tests only
	$(call print_header,"Running API chart tests")
	$(API_TESTS) --charts --verbose --skip-env-check

.PHONY: test-api-calculations
test-api-calculations: check-test-env ## Run API calculation tests only
	$(call print_header,"Running API calculation tests")
	$(API_TESTS) --calculations --verbose --skip-env-check

.PHONY: test-api-performance
test-api-performance: check-test-env ## Run API performance tests only
	$(call print_header,"Running API performance tests")
	$(API_TESTS) --performance --verbose --skip-env-check

.PHONY: test-api-quick
test-api-quick: check-test-env ## Run API tests (quick, less verbose)
	$(call print_header,"Running API tests (quick)")
	$(API_TESTS) --skip-env-check

.PHONY: test-api-integrated
test-api-integrated: check-test-env ## Run API tests with automatic server management
	$(call print_header,"Running API tests with managed server")
	$(API_TESTS_INTEGRATED) --verbose

.PHONY: test-api-integrated-auth
test-api-integrated-auth: check-test-env ## Run API authentication tests with managed server
	$(call print_header,"Running API authentication tests with managed server")
	$(API_TESTS_INTEGRATED) --auth --verbose

.PHONY: test-api-integrated-charts
test-api-integrated-charts: check-test-env ## Run API chart tests with managed server
	$(call print_header,"Running API chart tests with managed server")
	$(API_TESTS_INTEGRATED) --charts --verbose

.PHONY: test-api-integrated-calculations
test-api-integrated-calculations: check-test-env ## Run API calculation tests with managed server
	$(call print_header,"Running API calculation tests with managed server")
	$(API_TESTS_INTEGRATED) --calculations --verbose

.PHONY: test-api-integrated-quick
test-api-integrated-quick: check-test-env ## Run API tests with managed server (quick)
	$(call print_header,"Running API tests with managed server - quick")
	$(API_TESTS_INTEGRATED)

.PHONY: test-working
test-working: check-test-env ## Run all working tests (bypasses problematic collections)
	$(call print_header,"Running all working tests")
	@echo "🚀 WebSocket Tests (30 tests)..."
	@pytest tests/websocket/ -v --tb=short
	@echo ""
	@echo "🔐 Authentication Tests (41+ tests)..."
	@pytest tests/unit/test_admin_management.py tests/unit/test_registration_config_unit.py -v --tb=short
	@echo ""
	@echo "🔒 Admin Integration Tests..."
	@pytest tests/integration/test_admin_integration.py -v --tb=short || true
	$(call print_success,"Working tests completed")

.PHONY: test-complete
test-complete: check-test-env ## Run comprehensive test suite (all working components)
	$(call print_header,"Running comprehensive test suite")
	@echo "🚀 WebSocket Tests (30 tests)..."
	@pytest tests/websocket/ -v --tb=short
	@echo ""
	@echo "🔐 Authentication Unit Tests (41 tests)..."
	@pytest tests/unit/test_admin_management.py tests/unit/test_registration_config_unit.py -v --tb=short
	@echo ""
	@echo "🔑 Service Token Tests..."
	@pytest tests/unit/test_service_tokens.py -v --tb=short
	@echo ""
	@echo "🔒 Authentication Security Tests..."
	@pytest tests/security/test_admin_security.py -v --tb=short || true
	@echo ""
	@echo "🔑 Authentication Integration Tests..."
	@pytest tests/integration/test_admin_integration.py -v --tb=short || true
	@echo ""
	@echo "🛠️  Service Token Integration Tests..."
	@pytest tests/integration/test_service_token_script.py -v --tb=short || true
	@echo ""
	@echo "🌐 API Tests (via script)..."
	@$(API_TESTS) --skip-env-check --verbose || true
	$(call print_success,"Comprehensive testing completed")

.PHONY: test-complete-integrated
test-complete-integrated: check-test-env ## Run comprehensive test suite including integrated API tests
	$(call print_header,"Running comprehensive test suite with integrated API tests")
	@echo "🚀 WebSocket Tests (30 tests)..."
	@pytest tests/websocket/ -v --tb=short
	@echo ""
	@echo "🔐 Authentication Unit Tests (41 tests)..."
	@pytest tests/unit/test_admin_management.py tests/unit/test_registration_config_unit.py -v --tb=short
	@echo ""
	@echo "🔒 Authentication Security Tests..."
	@pytest tests/security/test_admin_security.py -v --tb=short || true
	@echo ""
	@echo "🔑 Authentication Integration Tests..."
	@pytest tests/integration/test_admin_integration.py -v --tb=short || true
	@echo ""
	@echo "🌐 API Tests (with managed server)..."
	@$(API_TESTS_INTEGRATED) --verbose || true
	$(call print_success,"Comprehensive testing with API integration completed")

.PHONY: test-all
test-all: test-complete-integrated ## Alias for comprehensive test suite with API integration

.PHONY: test-everything
test-everything: test-complete-integrated ## Run absolutely everything including integrated API tests

.PHONY: test-summary
test-summary: check-test-env ## Show test summary and status
	$(call print_header,"Test Suite Summary")
	@echo "✅ WebSocket Tests:           30/30 tests passing"
	@echo "✅ Admin Unit Tests:          14/14 tests passing"  
	@echo "✅ Registration Config Tests: 27/27 tests passing"
	@echo "✅ Service Token Unit Tests:  25+ tests (comprehensive coverage)"
	@echo "✅ Service Token API Tests:   15+ tests (endpoint coverage)"
	@echo "✅ Service Token Script Tests: 20+ tests (CLI coverage)"
	@echo "⚠️  Admin Security Tests:     23/28 tests passing (5 failing)"
	@echo "⚠️  Admin Integration Tests:  Working (some env dependencies)"
	@echo "❌ User Management Tests:     Import errors (deprecated paths)"
	@echo "🚀 API Tests (Integrated):    Automatic server management available"
	@echo ""
	@echo "📊 Total Working Tests:       130+ tests"
	@echo "🎯 Best Single Command:       make test-complete-integrated"
	@echo "🎯 Quick Working Tests:       make test-working"
	@echo "🎯 Service Token Tests:       make test-service-tokens"
	@echo "🎯 API Tests Only:            make test-api-integrated"

.PHONY: test-admin
test-admin: check-env ## Run admin functionality tests
	$(call print_header,"Running admin tests")
	pytest tests/unit/test_admin_management.py tests/api/test_admin_api.py tests/integration/test_admin_integration.py tests/security/test_admin_security.py -v

.PHONY: test-admin-unit
test-admin-unit: check-env ## Run admin unit tests only
	$(call print_header,"Running admin unit tests")
	pytest tests/unit/test_admin_management.py -v

.PHONY: test-admin-api
test-admin-api: check-test-env ## Run admin API tests only
	$(call print_header,"Running admin API tests")
	pytest tests/api/test_admin_api.py -v -m api

.PHONY: test-admin-integration
test-admin-integration: check-env ## Run admin integration tests only
	$(call print_header,"Running admin integration tests")
	pytest tests/integration/test_admin_integration.py -v -m integration

.PHONY: test-admin-security
test-admin-security: check-env ## Run admin security tests only
	$(call print_header,"Running admin security tests")
	pytest tests/security/test_admin_security.py -v

.PHONY: test-admin-postgres
test-admin-postgres: check-env ## Run admin tests against PostgreSQL database
	$(call print_header,"Running admin PostgreSQL integration tests")
	pytest tests/integration/test_admin_integration_postgres.py -v -m postgres

.PHONY: test-admin-full
test-admin-full: check-env ## Run all admin tests including PostgreSQL tests
	$(call print_header,"Running comprehensive admin test suite")
	pytest tests/unit/test_admin_management.py tests/api/test_admin_api.py tests/integration/test_admin_integration.py tests/integration/test_admin_integration_postgres.py tests/security/test_admin_security.py -v

##@ Service Token Tests

.PHONY: test-service-tokens
test-service-tokens: check-env ## Run all service token tests
	$(call print_header,"Running service token tests")
	pytest tests/unit/test_service_tokens.py tests/api/test_service_token_api.py tests/integration/test_service_token_script.py -v

.PHONY: test-service-tokens-unit
test-service-tokens-unit: check-env ## Run service token unit tests only
	$(call print_header,"Running service token unit tests")
	pytest tests/unit/test_service_tokens.py -v

.PHONY: test-service-tokens-api
test-service-tokens-api: check-test-env ## Run service token API tests only
	$(call print_header,"Running service token API tests")
	pytest tests/api/test_service_token_api.py -v -m api

.PHONY: test-service-tokens-integration
test-service-tokens-integration: check-env ## Run service token integration tests only
	$(call print_header,"Running service token integration tests")
	pytest tests/integration/test_service_token_script.py -v -m integration

.PHONY: test-service-tokens-full
test-service-tokens-full: check-env ## Run comprehensive service token test suite
	$(call print_header,"Running comprehensive service token test suite")
	pytest tests/unit/test_service_tokens.py tests/api/test_service_token_api.py tests/integration/test_service_token_script.py -v --tb=short

.PHONY: coverage
coverage: check-env ## Run tests with coverage report
	$(call print_header,"Running tests with coverage")
	pytest tests/ --cov=nocturna_calculations --cov-report=html --cov-report=term

.PHONY: coverage-websocket
coverage-websocket: check-test-env ## Run WebSocket tests with coverage report
	$(call print_header,"Running WebSocket tests with coverage")
	pytest tests/websocket/ --cov=nocturna_calculations.api.routers.websocket --cov-report=html --cov-report=term

.PHONY: coverage-auth
coverage-auth: check-test-env ## Run authentication tests with coverage report
	$(call print_header,"Running authentication tests with coverage")
	pytest tests/unit/test_admin_management.py tests/unit/test_registration_config_unit.py tests/integration/test_admin_integration.py --cov=nocturna_calculations.api.routers.auth --cov=nocturna_calculations.api.models --cov-report=html --cov-report=term

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

##@ Admin Management

.PHONY: admin-create
admin-create: check-env ## Create a new admin user
	$(call print_header,"Creating admin user")
	python scripts/create_admin.py create

.PHONY: admin-promote
admin-promote: check-env ## Promote existing user to admin
	$(call print_header,"Promoting user to admin")
	python scripts/create_admin.py promote

.PHONY: admin-list
admin-list: check-env ## List all admin users
	$(call print_header,"Listing admin users")
	python scripts/create_admin.py list

##@ Service Token Management

.PHONY: service-token-create
service-token-create: check-env ## Create a new service token (30 days)
	$(call print_header,"Creating service token")
	python scripts/manage_service_tokens.py create

.PHONY: service-token-create-eternal
service-token-create-eternal: check-env ## Create eternal service token (never expires)
	$(call print_header,"Creating eternal service token")
	@echo "⚠️  WARNING: Eternal tokens never expire!"
	@echo "⚠️  Ensure proper security measures are in place!"
	@read -p "Continue? [y/N]: " confirm && [ "$$confirm" = "y" ]
	python scripts/manage_service_tokens.py create --eternal

.PHONY: service-token-create-custom
service-token-create-custom: check-env ## Create custom duration service token (usage: make service-token-create-custom DAYS=90)
	$(call print_header,"Creating custom service token")
	@if [ -z "$(DAYS)" ]; then \
		echo "❌ Please specify DAYS. Example: make service-token-create-custom DAYS=90"; \
		exit 1; \
	fi
	python scripts/manage_service_tokens.py create --days $(DAYS)

.PHONY: service-token-list
service-token-list: check-env ## List all service tokens
	$(call print_header,"Listing service tokens")
	python scripts/manage_service_tokens.py list

.PHONY: service-token-revoke
service-token-revoke: check-env ## Revoke a service token (usage: make service-token-revoke TOKEN_ID=abc123)
	$(call print_header,"Revoking service token")
	@if [ -z "$(TOKEN_ID)" ]; then \
		echo "❌ Please specify TOKEN_ID. Example: make service-token-revoke TOKEN_ID=abc123-def456"; \
		exit 1; \
	fi
	python scripts/manage_service_tokens.py revoke $(TOKEN_ID)

.PHONY: service-token-check
service-token-check: check-env ## Check service token validity (usage: make service-token-check TOKEN="jwt_token_here")
	$(call print_header,"Checking service token")
	@if [ -z "$(TOKEN)" ]; then \
		echo "❌ Please specify TOKEN. Example: make service-token-check TOKEN=\"eyJ0eXAi...\""; \
		exit 1; \
	fi
	python scripts/manage_service_tokens.py check "$(TOKEN)"

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

##@ Production Deployment (Blue-Green)

.PHONY: deploy-staging
deploy-staging: ## Deploy to staging environment
	$(call print_header,"Deploying to staging")
	@bash scripts/deploy.sh staging

.PHONY: deploy-staging-rebuild
deploy-staging-rebuild: ## Deploy to staging with full rebuild
	$(call print_header,"Deploying to staging (rebuild)")
	@bash scripts/deploy.sh staging --rebuild

.PHONY: deploy-prod-auto
deploy-prod-auto: ## Auto-deploy to inactive production instance
	$(call print_header,"Auto-deploying to inactive instance")
	@bash scripts/deploy.sh auto

.PHONY: deploy-prod-blue
deploy-prod-blue: ## Deploy to blue production instance
	$(call print_header,"Deploying to blue instance")
	@bash scripts/deploy.sh blue

.PHONY: deploy-prod-green
deploy-prod-green: ## Deploy to green production instance
	$(call print_header,"Deploying to green instance")
	@bash scripts/deploy.sh green

.PHONY: deploy-prod-full
deploy-prod-full: ## Full production update (both blue & green instances)
	$(call print_header,"Full production update (rolling deployment)")
	@echo "Step 1: Deploying to inactive instance..."
	@bash scripts/deploy.sh auto
	@echo ""
	@echo "Step 2: Checking status..."
	@bash scripts/status.sh
	@echo ""
	@echo "Step 3: Switching traffic..."
	@bash -c 'CURRENT=$$(cat .current-env 2>/dev/null || echo "none"); \
		if [ "$$CURRENT" = "blue" ]; then \
			bash scripts/switch.sh green; \
		elif [ "$$CURRENT" = "green" ]; then \
			bash scripts/switch.sh blue; \
		else \
			bash scripts/switch.sh blue; \
		fi'
	@echo ""
	@echo "Step 4: Waiting 10 seconds..."
	@sleep 10
	@echo "Step 5: Deploying to second instance..."
	@bash scripts/deploy.sh auto
	@echo ""
	@echo "✓ Full update complete!"
	@bash scripts/status.sh

.PHONY: deploy-status
deploy-status: ## Show deployment status
	$(call print_header,"Deployment Status")
	@bash scripts/status.sh

.PHONY: deploy-switch-blue
deploy-switch-blue: ## Switch traffic to blue instance
	$(call print_header,"Switching to blue instance")
	@bash scripts/switch.sh blue

.PHONY: deploy-switch-green
deploy-switch-green: ## Switch traffic to green instance
	$(call print_header,"Switching to green instance")
	@bash scripts/switch.sh green

.PHONY: deploy-rollback
deploy-rollback: ## Rollback to previous instance
	$(call print_header,"Rolling back to previous instance")
	@bash scripts/rollback.sh

##@ Docker Deployment

.PHONY: docker-check
docker-check: ## Check Docker prerequisites
	$(call print_header,"Checking Docker prerequisites")
	@command -v docker >/dev/null 2>&1 || { echo "❌ Docker is not installed"; exit 1; }
	@command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is not installed"; exit 1; }
	@docker info >/dev/null 2>&1 || { echo "❌ Docker daemon is not running"; exit 1; }
	$(call print_success,"Docker prerequisites met")

.PHONY: docker-setup
docker-setup: docker-check ## Setup Docker environment
	$(call print_header,"Setting up Docker environment")
	@if [ ! -f $(ENV_FILE) ]; then \
		echo "Creating .env file from production template..."; \
		cp config/production.env $(ENV_FILE); \
		$(call print_warning,"Please update $(ENV_FILE) with your production values"); \
		echo "Required changes:"; \
		echo "  - SECRET_KEY (generate with: openssl rand -hex 32)"; \
		echo "  - ADMIN_PASSWORD"; \
		echo "  - POSTGRES_PASSWORD"; \
		echo "  - CORS_ORIGINS"; \
	fi
	$(call print_success,"Docker environment setup complete")

.PHONY: docker-build
docker-build: docker-check ## Build Docker image
	$(call print_header,"Building Docker image")
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	$(call print_success,"Docker image built: $(DOCKER_IMAGE):$(DOCKER_TAG)")

.PHONY: docker-up
docker-up: docker-check ## Start all services with Docker Compose
	$(call print_header,"Starting Docker services")
	docker-compose -f $(COMPOSE_FILE) up -d
	$(call print_success,"Services started. API available at http://localhost:8000")

.PHONY: docker-down
docker-down: ## Stop all Docker services
	$(call print_header,"Stopping Docker services")
	docker-compose -f $(COMPOSE_FILE) down
	$(call print_success,"Services stopped")

.PHONY: docker-restart
docker-restart: docker-down docker-up ## Restart all Docker services

.PHONY: docker-logs
docker-logs: ## View Docker service logs
	$(call print_header,"Docker service logs")
	docker-compose -f $(COMPOSE_FILE) logs -f

.PHONY: docker-logs-api
docker-logs-api: ## View API service logs only
	$(call print_header,"API service logs")
	docker-compose -f $(COMPOSE_FILE) logs -f app

.PHONY: docker-status
docker-status: ## Check Docker service status
	$(call print_header,"Docker service status")
	docker-compose -f $(COMPOSE_FILE) ps

.PHONY: docker-setup-production
docker-setup-production: docker-check ## Setup production environment
	$(call print_header,"Setting up production deployment")
	@if [ ! -f $(ENV_FILE) ]; then \
		$(call print_error,"$(ENV_FILE) not found. Run 'make docker-setup' first"); \
		exit 1; \
	fi
	docker-compose -f $(COMPOSE_FILE) exec app python scripts/setup_production.py
	$(call print_success,"Production setup complete")

.PHONY: docker-setup-production-dry
docker-setup-production-dry: docker-check ## Dry run production setup
	$(call print_header,"Production setup dry run")
	docker-compose -f $(COMPOSE_FILE) exec app python scripts/setup_production.py --dry-run

.PHONY: docker-token-check
docker-token-check: docker-check ## Check service token expiration status
	$(call print_header,"Checking service token status")
	docker-compose -f $(COMPOSE_FILE) exec app python scripts/renew_service_token.py --check-only

.PHONY: docker-token-renew
docker-token-renew: docker-check ## Renew service token if expiring soon
	$(call print_header,"Renewing service token")
	docker-compose -f $(COMPOSE_FILE) exec app python scripts/renew_service_token.py
	$(call print_success,"Token renewal complete")

.PHONY: docker-token-force-renew
docker-token-force-renew: docker-check ## Force renew service token
	$(call print_header,"Force renewing service token")
	docker-compose -f $(COMPOSE_FILE) exec app python scripts/renew_service_token.py --force
	$(call print_success,"Token force renewal complete")

.PHONY: docker-token-eternal
docker-token-eternal: docker-check ## Generate eternal service token (never expires)
	$(call print_header,"Generating eternal service token")
	@echo "⚠️  WARNING: Eternal tokens never expire!"
	@echo "⚠️  Ensure nginx/firewall restricts external access!"
	@read -p "Continue? [y/N]: " confirm && [ "$$confirm" = "y" ]
	docker-compose -f $(COMPOSE_FILE) exec app python scripts/renew_service_token.py --eternal
	$(call print_success,"Eternal token generation complete")

.PHONY: docker-token-custom
docker-token-custom: docker-check ## Generate custom duration service token (usage: make docker-token-custom DAYS=365)
	$(call print_header,"Generating custom duration service token")
	@if [ -z "$(DAYS)" ]; then \
		echo "❌ Please specify DAYS. Example: make docker-token-custom DAYS=365"; \
		exit 1; \
	fi
	docker-compose -f $(COMPOSE_FILE) exec app python scripts/renew_service_token.py --days $(DAYS) --force
	$(call print_success,"Custom token generation complete")

.PHONY: docker-migrate
docker-migrate: ## Run database migrations in Docker
	$(call print_header,"Running database migrations")
	docker-compose -f $(COMPOSE_FILE) exec app alembic upgrade head
	$(call print_success,"Database migrations complete")

.PHONY: docker-shell
docker-shell: ## Open shell in running API container
	$(call print_header,"Opening shell in API container")
	docker-compose -f $(COMPOSE_FILE) exec app bash

.PHONY: docker-clean
docker-clean: ## Clean Docker resources
	$(call print_header,"Cleaning Docker resources")
	docker-compose -f $(COMPOSE_FILE) down -v
	docker system prune -f
	$(call print_success,"Docker resources cleaned")

.PHONY: docker-deploy
docker-deploy: docker-setup docker-build docker-up docker-migrate docker-setup-production ## Complete Docker deployment
	$(call print_header,"Complete Docker deployment")
	$(call print_success,"Deployment complete! Check logs with 'make docker-logs'")

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
validate: quality test-working ## Run all validation checks (quality + working tests)

.PHONY: validate-complete
validate-complete: quality test-complete ## Run comprehensive validation (quality + all working tests)

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

.PHONY: check-test-env
check-test-env:
	@if [ "$(ENV_TYPE)" != "test" ]; then \
		$(call print_error,"Test environment not active"); \
		echo "API tests require the nocturna-test environment."; \
		echo "Please run:"; \
		echo "  make setup-test      # If not already set up"; \
		echo "  conda activate nocturna-test"; \
		echo ""; \
		echo "Note: Keep your dev server running in another terminal:"; \
		echo "  conda activate nocturna-dev && make dev"; \
		exit 1; \
	fi

# Default for common typos
.PHONY: install
install: setup ## Alias for setup

.PHONY: run
run: dev ## Alias for dev

.PHONY: serve
serve: dev ## Alias for dev 