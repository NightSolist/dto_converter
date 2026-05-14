.PHONY: help install build run clean test test-pipeline test-rust test-rust-unit test-rust-integration test-yaml test-all reset state-reset full-reset status

# Цвета для вывода
GREEN  := \033[0;32m
YELLOW := \033[0;33m
BLUE   := \033[0;34m
NC     := \033[0m

# Пути к репозиториям
RUST_REPO := $(HOME)/incus-lab-manager
GO_REPO   := $(HOME)/data/incus-fork-demo

# ============================================================
# Помощь
# ============================================================
help:
	@echo "$(BLUE)Incus Model Sync — Makefile commands$(NC)"
	@echo ""
	@echo "$(GREEN)Setup:$(NC)"
	@echo "  make install              — Setup Python venv + build Go AST parser"
	@echo "  make build                — Rebuild Go AST parser only"
	@echo ""
	@echo "$(GREEN)Run:$(NC)"
	@echo "  make run                  — Run full sync pipeline (monitor + generate + PR + CI)"
	@echo ""
	@echo "$(GREEN)Testing:$(NC)"
	@echo "  make test                 — Run all tests (pipeline + Rust unit + integration + YAML deploy)"
	@echo "  make test-pipeline        — Run only generator pipeline (no GitHub, no PR)"
	@echo "  make test-rust            — Run all Rust tests (unit + integration)"
	@echo "  make test-rust-unit       — Run Rust unit tests only (no Incus required)"
	@echo "  make test-rust-integration— Run Rust integration tests with real Incus"
	@echo "  make test-yaml            — Run full YAML lab deploy + destroy cycle"
	@echo ""
	@echo "$(GREEN)Cleanup:$(NC)"
	@echo "  make state-reset          — Reset only generator state (force re-sync)"
	@echo "  make reset                — Clean Incus + Rust target + reset state"
	@echo "  make full-reset           — Full cleanup: Incus + Rust + state + caches"
	@echo "  make clean                — Remove build artifacts (.venv, parser binary, __pycache__)"
	@echo ""
	@echo "$(GREEN)Diagnostics:$(NC)"
	@echo "  make status               — Show status of all components (Incus, Ollama, Woodpecker)"

# ============================================================
# Setup
# ============================================================
install:
	@echo "$(BLUE)==> Setting up Python virtual environment...$(NC)"
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -e ".[dev]"
	@echo "$(BLUE)==> Building Go AST Parser...$(NC)"
	cd src/go-ast-parser && go build -o parser main.go
	@echo "$(GREEN)==> Done! Run 'make run' to start generator.$(NC)"

build:
	@echo "$(BLUE)==> Building Go AST Parser...$(NC)"
	cd src/go-ast-parser && go build -o parser main.go
	@echo "$(GREEN)==> Done.$(NC)"

# ============================================================
# Run
# ============================================================
run:
	@echo "$(BLUE)==> Running Incus Model Sync Pipeline...$(NC)"
	python main.py

# ============================================================
# Testing
# ============================================================

# 1. Только генератор (pipeline без GitHub и Woodpecker)
test-pipeline:
	@echo "$(BLUE)==> [1/4] Testing generator pipeline (no GitHub)...$(NC)"
	@python -c "from src.pipeline import Pipeline; \
		ok = Pipeline().run(); \
		print('\n$(GREEN)✓ Pipeline OK$(NC)' if ok else '\n\033[0;31m✗ Pipeline FAILED\033[0m'); \
		exit(0 if ok else 1)"

# 2. Rust unit-тесты (без Incus)
test-rust-unit:
	@echo "$(BLUE)==> [2/4] Running Rust unit tests (DTO serialization)...$(NC)"
	cd $(RUST_REPO) && cargo test --test serde_dto -- --nocapture

# 3. Rust integration-тесты (с реальным Incus)
test-rust-integration:
	@echo "$(BLUE)==> [3/4] Running Rust integration tests (real Incus)...$(NC)"
	cd $(RUST_REPO) && cargo test --test integration_lab -- --nocapture --test-threads=1

# 4. YAML deploy + destroy
test-yaml:
	@echo "$(BLUE)==> [4/4] Testing YAML lab deploy + destroy...$(NC)"
	cd $(RUST_REPO) && cargo run --quiet -- deploy --file demo-lab.yaml
	@echo "$(YELLOW)→ Verifying deployed resources:$(NC)"
	@incus list | grep demo || echo "(no demo instances visible yet)"
	@echo "$(YELLOW)→ Destroying lab:$(NC)"
	cd $(RUST_REPO) && cargo run --quiet -- destroy --file demo-lab.yaml
	@echo "$(GREEN)✓ YAML deploy/destroy cycle OK$(NC)"

# Все Rust-тесты
test-rust: test-rust-unit test-rust-integration
	@echo "$(GREEN)✓ All Rust tests passed$(NC)"

# Полный набор тестов
test: test-pipeline test-rust-unit test-rust-integration test-yaml
	@echo ""
	@echo "$(GREEN)═══════════════════════════════════════════$(NC)"
	@echo "$(GREEN)✓ All tests passed successfully!$(NC)"
	@echo "$(GREEN)═══════════════════════════════════════════$(NC)"

# Алиас для совместимости с Python-конвенциями
test-all: test

# ============================================================
# Cleanup
# ============================================================

# Сбросить только state генератора
state-reset:
	@echo "$(BLUE)==> Resetting generator state...$(NC)"
	rm -f state/.sync_state state/changes.json
	@echo "$(GREEN)✓ State reset. Next run will re-sync from scratch.$(NC)"

# Удалить все Incus-ресурсы с префиксом demo-* и t<число>-*
reset-incus:
	@echo "$(BLUE)==> Cleaning up Incus resources from previous tests...$(NC)"
	@for inst in $$(incus list -c n -f csv 2>/dev/null | grep -E '^(demo-|t[0-9]+-)'); do \
		echo "  → deleting instance $$inst"; \
		incus delete $$inst --force 2>/dev/null || true; \
	done
	@for prof in $$(incus profile list -c n -f csv 2>/dev/null | grep -E '^(demo-|t[0-9]+-)'); do \
		echo "  → deleting profile $$prof"; \
		incus profile delete $$prof 2>/dev/null || true; \
	done
	@for net in $$(incus network list -c n -f csv 2>/dev/null | grep -E '^(demo-|t[0-9]+-)'); do \
		echo "  → deleting network $$net"; \
		incus network delete $$net 2>/dev/null || true; \
	done
	@for pool in $$(incus storage list -c n -f csv 2>/dev/null | grep -E '^(demo-|t[0-9]+-)'); do \
		echo "  → deleting storage pool $$pool"; \
		incus storage delete $$pool 2>/dev/null || true; \
	done
	@echo "$(GREEN)✓ Incus cleaned.$(NC)"

# Сброс state + Incus + target
reset: state-reset reset-incus
	@echo "$(BLUE)==> Cleaning Rust target...$(NC)"
	cd $(RUST_REPO) && cargo clean --quiet
	@echo "$(GREEN)✓ Reset complete.$(NC)"

# Полный сброс (всё, что reset, плюс Python-кэши и venv)
full-reset: reset clean
	@echo "$(GREEN)✓ Full reset complete. Run 'make install' to rebuild.$(NC)"

# Удалить артефакты сборки
clean:
	@echo "$(BLUE)==> Cleaning build artifacts...$(NC)"
	rm -rf .venv
	rm -rf src/*.egg-info
	rm -f src/go-ast-parser/parser
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ Cleaned.$(NC)"

# ============================================================
# Diagnostics
# ============================================================
status:
	@echo "$(BLUE)═══ System Status ═══$(NC)"
	@echo ""
	@echo "$(YELLOW)Incus:$(NC)"
	@incus --version 2>/dev/null && echo "  $(GREEN)✓ Available$(NC)" || echo "  ✗ Not installed"
	@echo ""
	@echo "$(YELLOW)Ollama:$(NC)"
	@curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1 && \
		echo "  $(GREEN)✓ Running on :11434$(NC)" || \
		echo "  ✗ Not responding"
	@echo ""
	@echo "$(YELLOW)Woodpecker:$(NC)"
	@curl -s http://localhost:8000/api/healthz > /dev/null 2>&1 && \
		echo "  $(GREEN)✓ Running on :8000$(NC)" || \
		echo "  ✗ Not responding"
	@echo ""
	@echo "$(YELLOW)Generator state:$(NC)"
	@if [ -f state/.sync_state ]; then \
		echo "  Last SHA: $$(cat state/.sync_state | head -c 12)..."; \
	else \
		echo "  (no state, will sync from scratch)"; \
	fi
	@echo ""
	@echo "$(YELLOW)Rust client:$(NC)"
	@if [ -d $(RUST_REPO) ]; then \
		echo "  $(GREEN)✓ Found at $(RUST_REPO)$(NC)"; \
		cd $(RUST_REPO) && echo "  Branch: $$(git branch --show-current)"; \
	else \
		echo "  ✗ Not found"; \
	fi