# README — incus-model-sync (generator)

---

## Обзор

`incus-model-sync` — система автоматической синхронизации моделей данных между Go-репозиторием [Incus](https://github.com/lxc/incus) и Rust-приложениями. При обнаружении изменений в Go-структурах система автоматически генерирует актуальные Rust DTO, валидирует их компилятором и публикует Pull Request в целевой Rust-репозиторий.

Проект является частью ВКР по теме **"Автоматическая синхронизация моделей данных клиентской библиотеки Incus и Rust-приложений на основе гибридной генерации с локальными LLM"**.

### Ключевые свойства

- **Нет промежуточных схем** — работает напрямую с Go-исходниками
- **Гибридная генерация** — шаблон (Jinja2) + локальная LLM (Ollama)
- **Конфиденциальность** — LLM работает локально, код не покидает машину
- **Compile-time валидация** — каждый сгенерированный файл проходит `cargo check`
- **Полный цикл автоматизации** — от изменения в Go до email инженеру

---

## Архитектура

```
main.py
  └── run_monitor()              # Мониторинг изменений в Go-репозитории
        └── если есть изменения:
  └── Pipeline().run()           # Конвейер генерации
        ├── ASTParser            # Парсинг Go-структур через AST
        ├── Dispatcher           # Классификация: template / llm / manual
        ├── RustGenerator        # Шаблонная генерация (Jinja2)
        ├── LLMGenerator         # LLM-генерация (Ollama / Qwen2.5-Coder)
        └── RustValidator        # Валидация через cargo check
  └── GitHubPublisher.publish()  # Создание PR в Rust-репозиторий
  └── WoodpeckerTrigger          # Запуск CI/CD pipeline
  └── save_state()               # Обновление .sync_state
```

### Flow данных

```
Go-исходники (shared/api/*.go)
    ↓  Go AST Parser (бинарь)
    ↓  Python-обёртка (ASTParser)
GoStruct / GoEnum / GoAlias
    ↓  Dispatcher
    ├── простые структуры → RustGenerator (Jinja2)
    └── сложные структуры → LLMGenerator (Ollama)
         └── при ошибке → fallback → RustGenerator
    ↓  RustValidator (cargo check во временном проекте)
    ↓  GitHubPublisher (Git Tree API)
Pull Request
    ↓  WoodpeckerTrigger (REST API)
Woodpecker CI: cargo-check → cargo-fmt → cargo-test-unit → Email
```

---

## Структура проекта

```
incus-model-sync/
├── main.py                          # Точка входа, оркестрация
├── src/
│   ├── config.py                    # Конфигурация путей
│   ├── monitor.py                   # Мониторинг через GitHub API
│   ├── pipeline.py                  # Конвейер генерации
│   ├── dispatcher.py                # Классификация структур
│   ├── github_publisher.py          # Публикация PR (Git Tree API)
│   ├── woodpecker_trigger.py        # Триггер Woodpecker CI
│   ├── email_notifier.py            # Email-уведомление (резервный модуль)
│   ├── parser/
│   │   ├── base.py                  # Абстрактный интерфейс парсера
│   │   ├── factory.py               # Фабрика парсеров
│   │   ├── go_types.py              # Dataclasses: GoStruct, GoField, GoEnum, GoAlias, GoTag
│   │   ├── ast_parser.py            # Production-парсер (Go AST)
│   │   ├── regex_parser.py          # Legacy-парсер (regex, только struct)
│   │   └── go-ast-parser/
│   │       └── parser/
│   │           └── main.go          # Go-бинарь: парсинг через go/ast
│   ├── generator/
│   │   ├── rust_generator.py        # Шаблонный генератор (Jinja2)
│   │   ├── llm_generator.py         # LLM-генератор (Ollama)
│   │   └── type_mapping.py          # Маппинг типов Go → Rust
│   └── validation/
│       └── validator.py             # cargo check во временном Cargo-проекте
└── templates/
    ├── struct.rs.j2                 # Шаблон Rust struct
    ├── enum.rs.j2                   # Шаблон Rust enum
    └── mod.rs.j2                    # Шаблон mod.rs
```

---

## Требования

### Системные

- **ОС**: Linux (Ubuntu 22.04+ / Debian 12+)
- **Python**: 3.11+
- **Go**: 1.21+ (для сборки AST-парсера)
- **Rust**: 1.83+ (для валидации через `cargo check`)
- **Ollama**: с загруженной моделью `qwen2.5-coder:1.5b`

### Python-зависимости

```
PyGithub>=2.1
requests>=2.31
Jinja2>=3.1
python-dotenv>=1.0
```

Установка:

```bash
pip install -r requirements.txt
```

---

## Установка и настройка

### 1. Клонировать репозиторий

```bash
git clone https://github.com/NightSolist/incus-model-sync.git
cd incus-model-sync
```

### 2. Установить Python-зависимости

```bash
pip install -r requirements.txt
```

### 3. Собрать Go AST Parser

```bash
cd src/go-ast-parser/parser
go build -o parser .
cd ../../..
```

Проверить:

```bash
ls -la src/go-ast-parser/parser/parser
# -rwxr-xr-x ... parser
```

### 4. Установить и настроить Ollama

```bash
# Установка
curl -fsSL https://ollama.com/install.sh | sh

# Загрузка модели
ollama pull qwen2.5-coder:1.5b

# Проверка
ollama list
# должна быть qwen2.5-coder:1.5b
```

### 5. Клонировать Go-репозиторий Incus (форк)

```bash
mkdir -p ~/data
git clone https://github.com/NightSolist/incus-fork-demo.git ~/data/incus-fork-demo
```

### 6. Настроить переменные окружения

Создать файл `.env` в корне проекта:

```bash
nano .env
```

Содержимое:

```env
# GitHub
GITHUB_TOKEN=ghp_ваш_токен_здесь
INCUS_SOURCE_REPO=NightSolist/incus-fork-demo

# Путь к локальному клону Go-репозитория
INCUS_REPO_PATH=/home/dev/data/incus-fork-demo

# Woodpecker CI
WOODPECKER_URL=http://localhost:8000
WOODPECKER_TOKEN=ваш_woodpecker_token
WOODPECKER_REPO=NightSolist/incus-lab-manager
```

Права доступа:

```bash
chmod 600 .env
```

### 7. Проверить конфигурацию

```bash
# Проверить что AST-парсер работает
src/go-ast-parser/parser/parser -dir ~/data/incus-fork-demo/shared/api | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f'Packages: {len(data)}')
print(f'Structs:  {sum(len(p[\"structs\"] or []) for p in data)}')
print(f'Enums:    {sum(len(p[\"enums\"] or []) for p in data)}')
"
```

Ожидаемый вывод:

```
Packages: 1
Structs:  200+
Enums:    3+
```

---

## Использование

### Запуск полного цикла

```bash
cd ~/dto_converter/generator
python main.py
```

Что происходит:

1. Мониторинг новых коммитов в Go-репозитории
2. Если изменений нет — ранний выход
3. Парсинг `shared/api/*.go` через Go AST
4. Классификация структур: template / LLM / manual
5. Генерация Rust DTO (шаблон + LLM)
6. Валидация через `cargo check`
7. Публикация Pull Request в GitHub
8. Триггер Woodpecker CI pipeline
9. Обновление `.sync_state`

### Ожидаемый вывод успешного прогона

```
🔎 Проверяем новые изменения в репозитории Incus...
Найдено изменений: 1 файлов API, 0 файлов client/
🚀 Обнаружены изменения. Запускаем pipeline...
🧪 Prototype mode enabled. Output dir: .../generated_prototype
🔍 Parsing Go structures from .../shared/api...
🧪 Prototype whitelist enabled: 14/221 structs kept
🔀 Dispatching entities...
🧠 Структура NetworkPut отправлена в LLM-генерацию
...
🧠 LLM обрабатывает структуру: NetworkPut
   🤖 [LLM] Попытка 1/3 для NetworkPut...
✅ NetworkPut: Успех с попытки 1
🛠️  Validating all generated files...
✅ Validation passed! Saving 17 files...
🌐 Публикуем результат в GitHub...
🌿 Ветка создана: sync/auto-2026-05-07-143021
📬 Pull Request создан: https://github.com/.../pull/7
⚙️  Запускаем self-hosted Woodpecker CI/CD pipeline...
⚙️  Woodpecker pipeline запущен: http://localhost:8000/...
💾 .sync_state обновлён: abc1234...
```

### Принудительный повторный прогон

Если нужно перегенерировать без реальных изменений в Go:

```bash
# Сбросить состояние
rm .sync_state

# Запустить заново
python main.py
```

---

## Конфигурация pipeline

### Prototype Mode

В `src/pipeline.py` включён режим прототипа:

```python
PROTOTYPE_MODE = True
```

В этом режиме обрабатывается только `PROTOTYPE_STRUCT_WHITELIST` — 14 структур из 221:

| Группа | Структуры |
|---|---|
| Network | `Network`, `NetworkPut`, `NetworksPost` |
| Profile | `Profile`, `ProfilePut`, `ProfilesPost` |
| StoragePool | `StoragePool`, `StoragePoolPut`, `StoragePoolsPost` |
| Instance | `InstancePut`, `InstancesPost`, `InstanceSource`, `InstanceStatePut` |
| Operation | `Operation` |

### Классификация структур

```
Dispatcher
├── manual_types = {ConfigMap, DevicesMap}
│     └── пропускаются (написаны вручную)
├── простые структуры (без ConfigMap/DevicesMap в полях)
│     └── → RustGenerator (Jinja2)
└── сложные структуры (содержат ConfigMap или DevicesMap)
      ├── если в LLM_TEST_WHITELIST → LLMGenerator
      └── иначе → fallback → RustGenerator
```

### LLM Whitelist

Через LLM обрабатываются только 5 структур из 14:

```python
LLM_TEST_WHITELIST = {
    "ProfilePut",
    "ProfilesPost",
    "InstancePut",
    "NetworkPut",
    "StoragePoolPut",
}
```

Остальные сложные структуры получают fallback на шаблонный генератор.

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

## LLM-генератор

### Модель

- **Ollama**: `qwen2.5-coder:1.5b`
- **Температура**: `0.1` (детерминированный вывод)
- **Максимум попыток**: `3`
- **Early-stop**: при повторении одной и той же ошибки

### Цепочка постобработки

После получения ответа от LLM применяются исправления:

1. `_split_use_statements()` — разбивает слипшиеся `use a;use b;` на отдельные строки
2. `_ensure_imports()` — добавляет недостающие `use crate::incus::ConfigMap/DevicesMap`
3. `_fix_int_types()` — заменяет `i32` на `i64` для полей с Go-типом `int`
4. `_ensure_pub_fields()` — добавляет `pub` к полям, если LLM забыла
5. `_check_forbidden_local_types()` — блокирует повторное объявление `ConfigMap`/`DevicesMap`

### Fallback

При ошибке LLM структура автоматически переключается на шаблонный генератор. Состояние `.sync_state` не обновляется при неудаче.

---

## Валидатор

Двухуровневая проверка:

### Уровень 1 — Синтаксическая проверка (быстрая)

Перед вызовом `cargo` проверяет:
- Отсутствие markdown-артефактов (` ``` `)
- Баланс скобок `{}`, `()`, `[]`
- Наличие объявления `pub struct/enum/type`

### Уровень 2 — Компиляционная валидация (cargo check)

```
Временный Cargo-проект в /tmp/
├── Cargo.toml (serde, chrono, serde_json)
└── src/
    ├── lib.rs
    └── incus/
        ├── mod.rs (+ заглушки ConfigMap/DevicesMap)
        └── *.rs (сгенерированные файлы)
```

Если `cargo check` прошёл — файлы сохраняются. Если нет — откат, `.sync_state` не обновляется.

---

## Мониторинг

### Что отслеживается

- `shared/api/*.go` — корневые Go-файлы API (только первый уровень, без подпакетов)
- `client/**/*.go` — файлы клиентской библиотеки

### Что игнорируется

- `shared/api/scriptlet/*.go` — подпакеты (не поддерживаются парсером)
- `*_test.go` — тестовые файлы

### Состояние

Хранится в `.sync_state` как SHA последнего успешно обработанного коммита:

```bash
cat .sync_state
# 817b0c8693df6afe59faf11bc02269417646368a
```

Обновляется **только** при успешном завершении полного цикла (PR создан + Woodpecker запущен).

---

## CI/CD интеграция

После публикации PR система автоматически запускает Woodpecker pipeline через REST API.

### Шаги Woodpecker pipeline (в Rust-репозитории)

| Шаг | Образ | Что делает |
|---|---|---|
| `cargo-check` | `rust:1.83` | Compile-time валидация всех DTO |
| `cargo-fmt` | `rust:1.83` | Проверка форматирования |
| `cargo-test-unit` | `rust:1.83` | Unit-тесты сериализации (8 тестов) |
| `notify-engineer` | `deblan/woodpecker-email` | Email при успехе |
| `notify-failure` | `deblan/woodpecker-email` | Email при ошибке |

### Безопасность

- Нет входящих соединений извне
- Нет туннелей через третьих провайдеров
- Весь трафик локальный
- Секреты хранятся в Woodpecker Secrets с `image-filter`

---

## Переменные окружения

| Переменная | Описание | Пример |
|---|---|---|
| `GITHUB_TOKEN` | Personal Access Token GitHub | `ghp_xxx` |
| `INCUS_SOURCE_REPO` | Go-репозиторий-источник | `NightSolist/incus-fork-demo` |
| `INCUS_REPO_PATH` | Локальный путь к Go-репозиторию | `/home/dev/data/incus-fork-demo` |
| `WOODPECKER_URL` | URL Woodpecker сервера | `http://localhost:8000` |
| `WOODPECKER_TOKEN` | Personal Access Token Woodpecker | `wp_xxx` |
| `WOODPECKER_REPO` | Rust-репозиторий в Woodpecker | `NightSolist/incus-lab-manager` |

---

## Устранение неполадок

### `Go AST tool not found`

```bash
# Пересобрать бинарь
cd src/go-ast-parser/parser
go build -o parser .
```

### `Ollama connection refused`

```bash
# Проверить что Ollama запущена
ollama list

# Запустить если нет
ollama serve &

# Проверить порт
curl http://127.0.0.1:11434/api/tags
```

### `GITHUB_TOKEN не задан`

```bash
# Проверить переменную
echo $GITHUB_TOKEN

# Загрузить из .env
export $(cat .env | xargs)
```

### `Изменений не обнаружено` при явном наличии изменений

```bash
# Сбросить состояние
rm .sync_state
python main.py
```

### LLM генерирует битый код несколько раз подряд

Это нормально — при повторении одной и той же ошибки срабатывает early-stop и структура переключается на шаблонный генератор. Итоговый файл будет корректным — просто без LLM.

### `cargo check` не найден

```bash
# Установить Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
cargo --version
```

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

---

## Связь с Rust-репозиторием

Этот генератор публикует результаты в [`incus-lab-manager`](https://github.com/NightSolist/incus-lab-manager) — Rust-клиент для управления лабораторными средами Incus.

Сгенерированные файлы попадают в:

```
incus-lab-manager/
└── src/
    └── incus/
        └── generated_prototype/   ← сюда
```

Ручные типы (`ConfigMap`, `DevicesMap`) хранятся в:

```
incus-lab-manager/
└── src/
    └── incus/
        └── custom/                ← эти не перезаписываются
```

---
