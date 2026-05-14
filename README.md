# Incus Model Sync

Автоматическая синхронизация моделей данных между Go-репозиторием [Incus](https://github.com/lxc/incus) и Rust-приложениями на основе гибридной генерации с локальными LLM.

Проект является частью ВКР по теме *"Автоматическая синхронизация моделей данных клиентской библиотеки Incus и Rust-приложений на основе гибридной генерации с локальными LLM"* (НИЯУ МИФИ, 10.04.01 «Информационная безопасность»).

---

## Что делает система

При обнаружении изменений в Go-структурах исходного репозитория Incus система автоматически:

1. Парсит изменённые Go-структуры через `go/ast`
2. Генерирует Rust DTO гибридным способом (шаблон + локальная LLM)
3. Валидирует результат через `cargo check`
4. Создаёт Pull Request в целевой Rust-репозиторий
5. Запускает self-hosted CI/CD pipeline (Woodpecker)
6. Отправляет email-уведомление инженеру

**Главный tagline:** *"Изменение в Go → автоматический Pull Request в Rust → уведомление инженеру"*

---

## Архитектура

```
┌─────────────────────────┐
│  Go repo (Incus fork)   │
│  shared/api/*.go        │
└───────────┬─────────────┘
            │ git push
            ▼
┌─────────────────────────┐
│  monitor.py             │  ← GitHub API
│  (find new commits)     │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Pipeline               │
│  ├── Go AST parser      │  ← src/go-ast-parser/parser (Go binary)
│  ├── Dispatcher         │  ← template / LLM / manual
│  ├── Rust generator     │  ← Jinja2 templates
│  ├── LLM generator      │  ← Ollama (qwen2.5-coder:1.5b)
│  └── Rust validator     │  ← cargo check (temp project)
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  GitHub Publisher       │  ← Git Tree API
│  (create PR)            │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Woodpecker CI          │
│  ├── cargo check        │
│  ├── cargo fmt          │
│  ├── cargo test (unit)  │
│  └── email notification │
└─────────────────────────┘
```

---

## Структура проекта

```
~/dto_converter/                       ← Этот репозиторий (generator)
├── main.py                            ← Точка входа
├── Makefile                           ← Все команды
├── pyproject.toml                     ← Python зависимости
├── README.md
├── .env                               ← Секреты (не в Git)
├── .gitignore
├── state/                             ← Runtime state (не в Git)
│   ├── .sync_state
│   └── changes.json
├── templates/                         ← Jinja2 шаблоны
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
    ├── email_notifier.py              ← Email (резервный канал)
    ├── parser/
    │   ├── ast_parser.py              ← Обёртка над Go AST
    │   ├── factory.py
    │   └── go_types.py
    ├── generator/
    │   ├── rust_generator.py          ← Шаблонная генерация
    │   ├── llm_generator.py           ← LLM-генерация
    │   └── type_mapping.py            ← Go → Rust типы
    ├── validation/
    │   └── validator.py               ← cargo check
    └── go-ast-parser/
        ├── main.go                    ← Go-парсер исходников
        └── parser                     ← Скомпилированный бинарник
```

**Связанные репозитории:**

```
~/incus-lab-manager/                   ← Целевой Rust-репозиторий
├── src/incus/
│   ├── custom/                        ← Ручные типы (ConfigMap, DevicesMap)
│   └── generated_prototype/           ← ← ← Генератор пишет сюда
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

---

## Установка

### 1. Установить системные зависимости

```bash
# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Go (если нет)
sudo apt install -y golang-go

# Incus (для integration-тестов)
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

# Создать .env с секретами
cat > .env << 'ENV_EOF'
INCUS_REPO_PATH=/home/dev/data/incus-fork-demo
INCUS_SOURCE_REPO=NightSolist/incus-fork-demo

GITHUB_TOKEN=ghp_your_token_here

WOODPECKER_URL=http://localhost:8000
WOODPECKER_TOKEN=your_woodpecker_token
WOODPECKER_REPO=NightSolist/incus-lab-manager
ENV_EOF

# Защитить файл
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

Должно показать ✅ для всех компонентов.

---

## Использование

### Основные команды

```bash
make help              # Список всех команд
make run               # Запустить полный цикл (monitor → generate → PR → CI)
make test              # Прогнать все тесты
make status            # Показать статус компонентов
```

### Запуск синхронизации

```bash
make run
```

Что произойдёт:
1. Запросит GitHub API на наличие новых коммитов в Go-репозитории
2. Если изменений нет — выйдет
3. Если есть — запустит pipeline генерации
4. Создаст PR в `incus-lab-manager`
5. Триггернёт Woodpecker pipeline
6. Email придёт после завершения CI

**Если хочешь форсировать прогон без реальных изменений:**
```bash
make state-reset    # Сбросить .sync_state
make run            # Pipeline увидит коммиты за 30 дней
```

---

## Тестирование

Прототип имеет **4 уровня тестирования**:

```bash
make test                    # Все 4 уровня сразу
```

Или по отдельности:

```bash
make test-pipeline           # 1. Только генератор (без GitHub)
make test-rust-unit          # 2. Rust unit-тесты сериализации DTO
make test-rust-integration   # 3. Rust integration с реальным Incus
make test-yaml               # 4. YAML deploy + destroy цикл
```

### Уровень 1: Pipeline (без сети)

Парсинг Go → генерация → валидация. Не требует GitHub API.

```bash
make test-pipeline
```

### Уровень 2: Unit-тесты Rust (без Incus)

Проверяет сериализацию/десериализацию DTO в JSON.

```bash
make test-rust-unit
```

### Уровень 3: Integration с реальным Incus

Создаёт storage pool, сеть, профиль и инстанс на реальном Incus, проверяет, что DTO работают, и удаляет всё.

```bash
make test-rust-integration
```

### Уровень 4: YAML deploy цикл

Разворачивает полную лабораторию из `demo-lab.yaml` (storage pool + сеть + профиль + 2 контейнера) и сносит её.

```bash
make test-yaml
```

---

## Очистка

```bash
make state-reset      # Сбросить только .sync_state (для повторного прогона)
make reset-incus      # Удалить все Incus-ресурсы demo-* и t<число>-*
make reset            # state-reset + reset-incus + cargo clean
make full-reset       # reset + удалить .venv, parser, __pycache__
make clean            # Только build artifacts (без Incus)
```

### Когда что использовать

| Сценарий | Команда |
|---|---|
| Хочу прогнать `make run` ещё раз | `make state-reset` |
| Тест упал, остались висящие ресурсы в Incus | `make reset-incus` |
| Хочу всё пересобрать с нуля | `make full-reset && make install` |
| Просто почистить мусор | `make clean` |

---

## Конфигурация

### Переменные окружения (`.env`)

| Переменная | Описание | Пример |
|---|---|---|
| `INCUS_REPO_PATH` | Путь к локальному клону Go-репо | `/home/dev/data/incus-fork-demo` |
| `INCUS_SOURCE_REPO` | GitHub-имя Go-репозитория | `NightSolist/incus-fork-demo` |
| `GITHUB_TOKEN` | Personal Access Token GitHub | `ghp_...` |
| `WOODPECKER_URL` | URL Woodpecker UI | `http://localhost:8000` |
| `WOODPECKER_TOKEN` | API-токен Woodpecker | `wp_...` |
| `WOODPECKER_REPO` | Целевой репозиторий в Woodpecker | `NightSolist/incus-lab-manager` |

### Prototype mode

В `src/pipeline.py` включён `PROTOTYPE_MODE = True`. Это означает:
- Обрабатывается только whitelist из 14 структур (не все 221)
- Файлы пишутся в `~/incus-lab-manager/src/incus/generated_prototype/`
- LLM используется только для подмножества из 5 структур (`LLM_TEST_WHITELIST`)

Whitelist структур:
```
Network, NetworkPut, NetworksPost,
Profile, ProfilePut, ProfilesPost,
StoragePool, StoragePoolPut, StoragePoolsPost,
InstancePut, InstancesPost,
InstanceSource, InstanceStatePut,
Operation
```

---

## Гибридная генерация

### Шаблонный путь (Jinja2)
- Для простых структур с примитивными типами
- 100% детерминированный
- Использует `templates/struct.rs.j2`, `enum.rs.j2`, `mod.rs.j2`

### LLM-путь (Ollama + Qwen2.5-Coder)
- Для сложных структур с `ConfigMap` / `DevicesMap`
- Локальная модель → код не уходит в облако
- Постобработка:
  - Разбивка слипшихся `use` 
  - Добавление недостающих импортов
  - Замена `i32` → `i64` для Go `int`
  - Добавление `pub` к полям
  - Запрет переопределения `ConfigMap`/`DevicesMap`
- Fallback на шаблон при ошибке LLM
- Early-stop при повторяющейся ошибке
- Максимум 3 попытки

### Manual типы
- `ConfigMap` и `DevicesMap` написаны вручную в Rust-репо
- Не перезаписываются генератором

---

## Метрики прототипа

| Метрика | Целевое | Достигнуто |
|---|---|---|
| Структур в prototype subset | ≥ 10 | **14** |
| Файлов на выходе (.rs) | — | **17** |
| LLM success rate | ≥ 80% | **100%** (5/5) |
| Время полного цикла | < 60 сек | **~30 сек** |
| Compile-time валидация | 100% | **100%** |
| Ручных правок после генерации | минимум | **0** |
| Self-hosted CI/CD | развёрнут | **Woodpecker v3** |
| Email-уведомление | работает | **SMTP mail.ru** |

---

## Безопасность

- **Конфиденциальность кода:** LLM (Qwen2.5-Coder) работает локально через Ollama, код не отправляется в облако
- **CI/CD:** Self-hosted Woodpecker, нет входящих соединений извне
- **Секреты:** Токены в `.env` (не в Git), Woodpecker secrets с image-filter
- **TLS:** Rust-клиент использует mTLS для подключения к Incus

---

## Troubleshooting

### `make run` падает с "Failed to resolve api.github.com"
Проблема с DNS. Проверь:
```bash
getent hosts api.github.com
curl -I https://api.github.com
```

### `make test-rust-integration` падает с "auth: untrusted"
Сертификат не в trust store Incus:
```bash
incus config trust add-certificate ~/incus-lab-manager/certs/client.crt --name incus-lab-manager
```

### `make test-yaml` падает с "Network interface is too long"
Имя сети больше 15 символов. В `demo-lab.yaml` имена должны быть короткими.

### Изменений не обнаружено при наличии новых коммитов
Сбрось state:
```bash
make state-reset
make run
```

### Ollama не отвечает
Проверь:
```bash
make status
ollama list
ollama serve  # если не запущен
```

---

## Лицензия

MIT

---

## Автор

ВКР, НИЯУ МИФИ, 2026
EOF
```

---

# Финальные шаги

### 1. Проверим, что всё работает

```bash
cd ~/dto_converter

# Проверить Makefile
make help

# Проверить статус системы
make status
```

### 2. Если выглядит хорошо — закоммитить

```bash
git add Makefile README.md
git commit -m "docs: comprehensive README and Makefile with test/cleanup commands

- Add structured help with grouped commands (Setup/Run/Testing/Cleanup/Diagnostics)
- Add 4-level testing: pipeline, rust-unit, rust-integration, yaml
- Add cleanup commands: state-reset, reset-incus, full-reset
- Add status command for diagnostics
- Comprehensive README with architecture diagram, setup, usage, troubleshooting"
git push origin main
```

### 3. Прогнать тестовый сценарий

```bash
make status
make test-pipeline
make test-rust-unit
```