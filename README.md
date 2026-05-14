# Incus Model Sync

Автоматическая синхронизация моделей данных между Go-репозиторием [Incus](https://github.com/lxc/incus) и Rust-приложениями на основе гибридной генерации с локальными LLM.

Проект является частью ВКР по теме *«Автоматическая синхронизация моделей данных клиентской библиотеки Incus и Rust-приложений на основе гибридной генерации с локальными LLM»*  
(НИЯУ МИФИ, 10.04.01 «Информационная безопасность»).

---

## Что делает система

При обнаружении изменений в Go-структурах исходного репозитория Incus система автоматически:

1. Мониторит новые коммиты в Go-репозитории через GitHub API
2. Парсит Go-структуры через `go/ast`
3. Генерирует Rust DTO гибридным способом:
   - шаблонная генерация (`Jinja2`)
   - локальная LLM (`Ollama`, `qwen2.5-coder:1.5b`)
4. Валидирует результат через `cargo check`
5. Создаёт Pull Request в целевой Rust-репозиторий
6. Запускает self-hosted CI/CD pipeline (`Woodpecker`)
7. Отправляет email-уведомление инженеру

**Главный tagline:**  
**«Изменение в Go → автоматический Pull Request в Rust → уведомление инженеру»**

---

## Ключевые свойства

- **Нет промежуточных схем** — работа напрямую с Go-исходниками
- **Гибридная генерация** — шаблонный путь + локальная LLM
- **Конфиденциальность** — код не покидает локальный контур
- **Compile-time validation** — результат проверяется компилятором Rust
- **Self-hosted CI/CD** — локальный Woodpecker без внешних webhook
- **Минимум ручного труда** — от изменения в Go до PR и уведомления

---

## Архитектура

```text
main.py
  └── run_monitor()                 # Мониторинг изменений в Go-репозитории
        └── если есть изменения:
  └── Pipeline().run()              # Конвейер генерации
        ├── ASTParser               # Парсинг Go-структур через AST
        ├── Dispatcher              # Классификация: template / llm / manual
        ├── RustGenerator           # Шаблонная генерация (Jinja2)
        ├── LLMGenerator            # LLM-генерация (Ollama / Qwen2.5-Coder)
        └── RustValidator           # Валидация через cargo check
  └── GitHubPublisher.publish()     # Создание Pull Request
  └── WoodpeckerTrigger             # Запуск CI/CD pipeline
  └── save_state()                  # Обновление state/.sync_state
```

### Поток данных

```text
Go repo (shared/api/*.go)
    ↓
monitor.py (GitHub API)
    ↓
Go AST parser
    ↓
Dispatcher
    ├── простые структуры → RustGenerator (Jinja2)
    └── сложные структуры → LLMGenerator (Ollama)
           └── при ошибке → fallback на шаблон
    ↓
RustValidator (cargo check во временном проекте)
    ↓
Локальная запись в:
~/incus-lab-manager/src/incus/generated_prototype
    ↓
GitHubPublisher (Git Tree API)
    ↓
Pull Request
    ↓
WoodpeckerTrigger (REST API)
    ↓
Woodpecker CI: cargo check → cargo fmt → email
```

---

## Структура проекта

```text
~/dto_converter/                       ← Этот репозиторий (generator)
├── main.py                            ← Точка входа
├── Makefile                           ← Основные команды
├── pyproject.toml                     ← Python-зависимости и конфигурация проекта
├── README.md
├── .env                               ← Секреты (не в Git)
├── .gitignore
├── state/                             ← Runtime-state
│   ├── .sync_state
│   └── changes.json
├── templates/                         ← Jinja2-шаблоны
│   ├── struct.rs.j2
│   ├── enum.rs.j2
│   └── mod.rs.j2
└── src/
    ├── config.py                      ← Конфигурация путей
    ├── monitor.py                     ← Мониторинг GitHub API
    ├── pipeline.py                    ← Оркестрация генерации
    ├── dispatcher.py                  ← template / llm / manual
    ├── github_publisher.py            ← Создание PR
    ├── woodpecker_trigger.py          ← Триггер CI
    ├── email_notifier.py              ← Резервный email-модуль
    ├── parser/
    │   ├── ast_parser.py              ← Обёртка над Go AST
    │   ├── factory.py
    │   ├── go_types.py
    │   ├── base.py
    │   └── regex_parser.py
    ├── generator/
    │   ├── rust_generator.py          ← Шаблонная генерация
    │   ├── llm_generator.py           ← LLM-генерация
    │   └── type_mapping.py            ← Go → Rust типы
    ├── validation/
    │   └── validator.py               ← cargo check
    └── go-ast-parser/
        ├── main.go                    ← Go AST parser
        ├── go.mod
        └── parser                     ← Скомпилированный бинарник
```

### Связанные репозитории

```text
~/incus-lab-manager/                   ← Целевой Rust-репозиторий
├── src/incus/
│   ├── custom/                        ← Ручные типы (ConfigMap, DevicesMap)
│   └── generated_prototype/           ← Генератор пишет сюда
├── tests/
│   ├── serde_dto.rs                   ← Unit-тесты сериализации
│   └── integration_lab.rs             ← Integration с реальным Incus
└── demo-lab.yaml                      ← Демо-сценарий

~/data/incus-fork-demo/                ← Локальный клон Go-репозитория
└── shared/api/*.go                    ← Источник истины
```

---

## Требования

### Системные

- **OS:** Linux (Ubuntu/Debian)
- **Python:** 3.11+
- **Rust:** 1.83+
- **Go:** 1.21+ (для сборки AST-парсера)
- **Incus:** 6.x (для integration-тестов)

### Внешние сервисы

- **Ollama** с моделью `qwen2.5-coder:1.5b` (локально)
- **Woodpecker CI** v3.x (Docker, локально)
- **GitHub** аккаунт + Personal Access Token

### Важно

Проект **не использует `requirements.txt`**.  
Python-зависимости управляются через `pyproject.toml`.

---

## Установка

### 1. Установить системные зависимости

```bash
# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Go
sudo apt install -y golang-go

# Incus
# См. https://linuxcontainers.org/incus/docs/main/installing/

# Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5-coder:1.5b
```

### 2. Клонировать все три репозитория

```bash
# Generator (этот репозиторий)
cd ~
git clone https://github.com/<your-username>/dto_converter.git

# Rust client (целевой)
git clone https://github.com/NightSolist/incus-lab-manager.git

# Go source (форк Incus)
mkdir -p ~/data
cd ~/data
git clone https://github.com/NightSolist/incus-fork-demo.git
```

### 3. Настроить generator

```bash
cd ~/dto_converter

# Установить Python-зависимости и собрать Go-парсер
make install

# Создать .env
cat > .env << 'ENV_EOF'
INCUS_REPO_PATH=/home/dev/data/incus-fork-demo
INCUS_SOURCE_REPO=NightSolist/incus-fork-demo

GITHUB_TOKEN=ghp_your_token_here

WOODPECKER_URL=http://localhost:8000
WOODPECKER_TOKEN=your_woodpecker_token
WOODPECKER_REPO=NightSolist/incus-lab-manager
ENV_EOF

chmod 600 .env
```

### 4. Настроить Rust client

```bash
cd ~/incus-lab-manager

# Сгенерировать клиентский сертификат для Incus
mkdir -p certs
openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 -nodes \
  -keyout certs/client.key -out certs/client.crt \
  -subj "/CN=incus-lab-manager-client"
chmod 600 certs/client.key

# Добавить сертификат в trust store Incus
incus config trust add-certificate certs/client.crt --name incus-lab-manager

# Скачать образ для тестов
incus image copy images:alpine/3.21 local: --alias alpine-3.21
```

### 5. Проверить готовность

```bash
cd ~/dto_converter
make status
```

Должно показать, что доступны:
- Incus
- Ollama
- Woodpecker
- Rust client
- generator state

---

## Основные команды

```bash
make help              # Список всех команд
make run               # Полный цикл: monitor → generate → PR → CI
make test              # Все 4 уровня тестирования
make status            # Статус компонентов
make install           # Установка Python env + сборка Go parser
make build             # Только пересборка Go parser
```

---

## Использование

### Запуск полного цикла

```bash
make run
```

Что произойдёт:

1. Запрос к GitHub API на наличие новых коммитов
2. Если изменений нет — ранний выход
3. Если есть — запуск pipeline генерации
4. Создание PR в `incus-lab-manager`
5. Триггер Woodpecker pipeline
6. Email после завершения CI

### Принудительный повторный прогон

```bash
make state-reset
make run
```

---

## Тестирование

Прототип имеет **4 уровня тестирования**:

```bash
make test
```

Или по отдельности:

```bash
make test-pipeline
make test-rust-unit
make test-rust-integration
make test-yaml
```

### Уровень 1 — Pipeline (без GitHub)

Парсинг Go → генерация → валидация.  
Не требует GitHub API, PR и Woodpecker.

```bash
make test-pipeline
```

### Уровень 2 — Rust unit-тесты

Проверяет сериализацию и DTO-контракты.

```bash
make test-rust-unit
```

### Уровень 3 — Integration с реальным Incus

Создаёт storage pool, сеть, профиль и инстанс на реальном Incus, затем удаляет их.

```bash
make test-rust-integration
```

### Уровень 4 — YAML deploy / destroy

Разворачивает лабораторию из `demo-lab.yaml`, затем полностью удаляет её.

```bash
make test-yaml
```

---

## Очистка

```bash
make state-reset      # Сбросить только state генератора
make reset-incus      # Удалить ресурсы Incus demo-* и t<число>-*
make reset            # state-reset + reset-incus + cargo clean
make full-reset       # reset + удалить .venv, parser, __pycache__
make clean            # Только build artifacts
```

### Когда что использовать

| Сценарий | Команда |
|---|---|
| Хочу заново запустить `make run` | `make state-reset` |
| После тестов остались ресурсы в Incus | `make reset-incus` |
| Хочу всё пересобрать с нуля | `make full-reset && make install` |
| Просто почистить build-артефакты | `make clean` |

---

## Конфигурация

### Переменные окружения (`.env`)

| Переменная | Описание | Пример |
|---|---|---|
| `INCUS_REPO_PATH` | Путь к локальному клону Go-репозитория | `/home/dev/data/incus-fork-demo` |
| `INCUS_SOURCE_REPO` | GitHub-имя Go-репозитория | `NightSolist/incus-fork-demo` |
| `GITHUB_TOKEN` | GitHub Personal Access Token | `ghp_...` |
| `WOODPECKER_URL` | URL Woodpecker UI | `http://localhost:8000` |
| `WOODPECKER_TOKEN` | API-токен Woodpecker | `wp_...` |
| `WOODPECKER_REPO` | Целевой репозиторий в Woodpecker | `NightSolist/incus-lab-manager` |

---

## Prototype mode

В `src/pipeline.py` включён `PROTOTYPE_MODE = True`. Это означает:

- обрабатывается только whitelist из 14 структур;
- генерация пишется в `~/incus-lab-manager/src/incus/generated_prototype/`;
- LLM используется только для стабильного подмножества структур.

### Prototype whitelist

```text
Network, NetworkPut, NetworksPost,
Profile, ProfilePut, ProfilesPost,
StoragePool, StoragePoolPut, StoragePoolsPost,
InstancePut, InstancesPost,
InstanceSource, InstanceStatePut,
Operation
```

### LLM whitelist

```text
ProfilePut
ProfilesPost
InstancePut
NetworkPut
StoragePoolPut
```

### Manual types

Следующие типы написаны вручную в Rust-репозитории и не перезаписываются:

- `ConfigMap`
- `DevicesMap`

---

## Гибридная генерация

### Шаблонный путь (Jinja2)

- для простых структур с примитивными типами;
- полностью детерминированный;
- использует:
  - `templates/struct.rs.j2`
  - `templates/enum.rs.j2`
  - `templates/mod.rs.j2`

### LLM-путь (Ollama + Qwen2.5-Coder)

- для сложных структур с `ConfigMap` / `DevicesMap`;
- локальная модель, код не уходит в облако;
- включает постобработку:
  - разбивка слипшихся `use`
  - добавление недостающих импортов
  - замена `i32` → `i64` для Go `int`
  - добавление `pub` к полям
  - запрет переопределения `ConfigMap`/`DevicesMap`

### Fallback

- при ошибке LLM выполняется fallback на шаблон;
- при повторяющейся ошибке срабатывает early-stop;
- максимум 3 попытки.

---

## Маппинг типов Go → Rust

| Go | Rust |
|---|---|
| `string` | `String` |
| `int` | `i64` |
| `int64` | `i64` |
| `int32` | `i32` |
| `uint64` | `u64` |
| `float64` | `f64` |
| `bool` | `bool` |
| `[]T` | `Vec<T>` |
| `*T` | `Option<T>` |
| `map[string]string` | `ConfigMap` |
| `map[string]map[string]string` | `DevicesMap` |
| `map[K]V` | `HashMap<K, V>` |
| `time.Time` | `chrono::DateTime<chrono::Utc>` |
| `interface{}` / `any` | `serde_json::Value` |

### Обработка serde-тегов

| Go-тег | Результат в Rust |
|---|---|
| `json:"name"` | `#[serde(rename = "name")]` |
| `json:"name,omitempty"` | `Option<T>` + `#[serde(skip_serializing_if = "Option::is_none")]` |
| `yaml:",inline"` | `#[serde(flatten)]` |
| Поле `type` | `r#type` |

---

## Валидация

Реализована двухуровневая проверка.

### Уровень 1 — локальная compile-time validation

Генератор создаёт временный Cargo-проект и запускает:

```bash
cargo check --message-format=json
```

Если проверка не проходит:
- pipeline откатывается;
- `.sync_state` не обновляется;
- PR не создаётся.

### Уровень 2 — CI/CD

После публикации PR Woodpecker проверяет целевой Rust-репозиторий целиком:

- `cargo check --all-targets`
- `cargo fmt --all --check`
- email при success / failure

---

## Мониторинг

### Что отслеживается

- `shared/api/*.go`
- `client/**/*.go`

### Что игнорируется

- подпакеты вроде `shared/api/scriptlet/*.go`
- `*_test.go`

### State

Состояние последнего успешно обработанного коммита хранится в:

```text
state/.sync_state
```

Информация о последнем запуске мониторинга сохраняется в:

```text
state/changes.json
```

---

## CI/CD

После успешной генерации система автоматически:

1. создаёт Pull Request в `NightSolist/incus-lab-manager`
2. триггерит Woodpecker pipeline через REST API
3. отправляет email инженеру после завершения CI

### Почему self-hosted

- нет входящих соединений извне
- нет туннелей через third-party сервисы
- весь трафик остаётся в локальном периметре
- соблюдаются требования по конфиденциальности

---

## Метрики прототипа

| Метрика | Целевое | Достигнуто |
|---|---|---|
| Структур в prototype subset | ≥ 10 | **14** |
| Файлов на выходе (.rs) | — | **17** |
| LLM success rate | ≥ 80% | **100% (5/5)** |
| Время полного цикла | < 60 сек | **~30 сек** |
| Compile-time валидация | 100% | **100%** |
| Ручных правок после генерации | минимум | **0** |
| Self-hosted CI/CD | развёрнут | **Woodpecker v3** |
| Email-уведомление | работает | **SMTP mail.ru** |

---

## Безопасность

- **Конфиденциальность кода:** LLM работает локально через Ollama
- **CI/CD:** self-hosted Woodpecker
- **Секреты:** токены в `.env`, email-учётные данные — в Woodpecker Secrets
- **TLS:** Rust-клиент использует mTLS для подключения к Incus
- **Локальный периметр:** без внешних входящих webhook

---

## Troubleshooting

### `make run` падает с `Failed to resolve api.github.com`

Проверь DNS:

```bash
getent hosts api.github.com
curl -I https://api.github.com
```

### `make test-rust-integration` падает с `auth: untrusted`

Добавь клиентский сертификат в trust store Incus:

```bash
incus config trust add-certificate ~/incus-lab-manager/certs/client.crt --name incus-lab-manager
```

### `make test-yaml` падает с ошибкой длины интерфейса

Имена сетей в `demo-lab.yaml` должны быть короткими.

### `Изменений не обнаружено`, хотя коммиты есть

```bash
make state-reset
make run
```

### Ollama не отвечает

```bash
make status
ollama list
ollama serve
```

### Нужно пересобрать parser

```bash
make build
```

### Сломалось Python-окружение

```bash
make full-reset
make install
```

---

## Связь с Rust-репозиторием

Результаты генерации публикуются в:

- `NightSolist/incus-lab-manager`

Сгенерированные файлы попадают в:

```text
src/incus/generated_prototype/
```

Ручные типы (`ConfigMap`, `DevicesMap`) находятся в:

```text
src/incus/custom/
```

и **не перезаписываются** генератором.
