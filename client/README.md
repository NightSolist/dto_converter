# Incus Lab Manager (Rust Client)

![Rust](https://img.shields.io/badge/Rust-1.78+-orange)
![Incus](https://img.shields.io/badge/Incus-6.0+-blue)

**incus-lab-manager** — Утилита командной строки для автоматизированного развертывания и управления лабораториями на базе контейнеров Incus.

Особенность данного проекта — **полное использование автоматически сгенерированных DTO** (Data Transfer Objects) из официального Go-репозитория Incus.

---

## 📖 Описание (Description)

Утилита позволяет разворачивать изолированные среды (сети, инстансы) на основе декларативных YAML-конфигураций, а также управлять жизненным циклом отдельных контейнеров по mTLS каналу.

В качестве моделей данных (`src/incus/*.rs`) используются структуры, созданные генератором `incus-model-sync` на основе AST-анализа исходного кода сервера.

---

## ⚙️ Синтаксис (Synopsis)

```bash
cargo run -- <COMMAND> [OPTIONS]
```

*(Если бинарник скомпилирован: `./incus-lab-manager <COMMAND> [OPTIONS]`)*

---

## 🛠 Команды (Commands)

| Команда | Описание | Пример использования |
| :--- | :--- | :--- |
| `deploy` | Развернуть инфраструктуру лаборатории на основе YAML-файла. Автоматически создает сети и запускает контейнеры/ВМ. | `cargo run -- deploy --file labs/test.yaml` |
| `destroy` | Уничтожить всю инфраструктуру лаборатории, описанную в YAML-файле. (Идемпотентна). | `cargo run -- destroy --file labs/test.yaml` |
| `start` | Запустить конкретный остановленный инстанс (контейнер или ВМ). | `cargo run -- start <NAME>` |
| `stop` | Принудительно (force) остановить работающий инстанс. | `cargo run -- stop <NAME>` |
| `delete` | Удалить инстанс из Incus. Если инстанс запущен, он будет остановлен. | `cargo run -- delete <NAME>` |
| `info` | Проверить соединение с сервером Incus и вывести информацию об окружении. | `cargo run -- info` |

---

## 🎛 Параметры (Options)

*   `-f, --file <FILE>` — Путь к файлу конфигурации лаборатории в формате YAML. Требуется для команд `deploy` и `destroy`.
*   `-h, --help` — Вывести справочную информацию по утилите или конкретной команде.
*   `-V, --version` — Вывести версию утилиты.

---

## 📄 Формат Конфигурации (Configuration Format)

Утилита ожидает YAML файл со следующей структурой:

```yaml
name: "Имя лаборатории"
description: "Опциональное описание"

# Описание изолированных сетей
networks:
  - name: my-net
    ipv4: 10.0.0.1/24

# Описание инстансов (виртуальных машин и контейнеров)
instances:
  - name: my-container
    type: container          # 'container' или 'virtual-machine'
    image: images:alpine/3.20 # Поддерживает удаленные алиасы (simplestreams)
    network: my-net          # Привязка к созданной сети
    start: true              # Запускать ли после создания (default: false)
    profiles: [default]
```

---

## 🔐 Аутентификация (Authentication)

Утилита использует **mTLS** для подключения к серверу Incus (по умолчанию `https://127.0.0.1:8443`).

Требуется наличие клиентских сертификатов в рабочей директории:
*   `certs/client.crt`
*   `certs/client.key`

Данный сертификат должен быть предварительно добавлен в доверенные на сервере Incus:
```bash
sudo incus config trust add-certificate certs/client.crt --name incus-lab-manager
```

---

## 💡 Примеры (Examples)

**1. Проверить доступность API сервера:**
```bash
cargo run -- info
```

**2. Развернуть лабораторию из файла:**
```bash
cargo run -- deploy -f labs/test-lab.yaml
```

**3. Остановить конкретный контейнер:**
```bash
cargo run -- stop web-server
```

**4. Удалить всю лабораторию:**
```bash
cargo run -- destroy -f labs/test-lab.yaml
```

---

## 👨‍💻 Авторы (Authors)
Разработано в рамках исследовательского проекта по автоматизации DevSecOps и межъязыковой синхронизации API моделей.