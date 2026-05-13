.PHONY: install build test run clean

# Настройка Python окружения и сборка Go-парсера
install:
	@echo "==> Setting up Python virtual environment..."
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -e ".[dev]"
	@echo "==> Building Go AST Parser..."
	cd src/go-ast-parser && go build -o parser main.go
	@echo "==> Done! Run 'make run' to start generator."

# Только пересборка Go-парсера (если менял код на Go)
build:
	@echo "==> Building Go AST Parser..."
	cd src/go-ast-parser && go build -o parser main.go

# Запуск пайплайна генерации
run:
	@echo "==> Running Incus Model Sync Pipeline..."
	.venv/bin/python main.py

# Очистка мусора
clean:
	@echo "==> Cleaning up..."
	rm -rf .venv
	rm -rf src/*.egg-info
	rm -f src/go-ast-parser/parser
	find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "==> Cleaned."