.PHONY: build run check clean certs

# Компиляция проекта
build:
	@echo "==> Building Rust Client..."
	cargo build

# Проверка синтаксиса
check:
	@echo "==> Checking Rust code..."
	cargo check

# Запуск приложения (показывает info)
run:
	@echo "==> Running Incus Lab Manager (Info mode)..."
	cargo run -- info

# Генерация сертификатов для тестирования
certs:
	@echo "==> Generating client certificates..."
	mkdir -p certs
	openssl genrsa -out certs/client.key 4096
	openssl req -new -x509 -key certs/client.key -out certs/client.crt -days 365 -subj "/CN=incus-lab-manager"
	@echo "==> Certificates generated in ./certs/"
	@echo "==> Don't forget to run: sudo incus config trust add-certificate certs/client.crt --name incus-lab-manager"

# Очистка
clean:
	@echo "==> Cleaning Rust target..."
	cargo clean
	rm -rf certs