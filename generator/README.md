# Incus Model Sync (AST Generator)

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Go](https://img.shields.io/badge/Go-1.22+-cyan)

**incus-model-sync** — Ядро автоматизации конвейера. Это пайплайн кодогенерации, который читает исходный код сервера Incus (Golang) и автоматически генерирует строго типизированные модели данных (DTO) для клиентских приложений на языке Rust.

---

## 📖 Описание (Description)

Данный инструмент решает проблему рассинхронизации клиентских библиотек при изменении серверного API. Вместо ручного переписывания структур данных, генератор использует **синтаксический анализ кода (AST)** для 100% точной трансляции Go-типов в Rust-типы.

### Основные возможности:
*   **Go AST Parser:** Использует стандартную библиотеку `go/parser` для точного извлечения структур, перечислений (`const` блоков) и псевдонимов типов (aliases).
*   **Embedded Structs Flattening:** Автоматически "разворачивает" встроенные структуры Go (`yaml:",inline"`) в плоские поля Rust, сохраняя совместимость JSON.
*   **Enum Serialization:** Распознает значения констант и применяет макросы `#[serde(rename="...")]` для корректной сериализации.
*   **Type Aliasing:** Транслирует сложные типы (например, `map[string]map[string]string`) во вложенные `HashMap`.
*   **Auto-Validation:** Проверяет весь сгенерированный Rust-код компилятором `cargo check` перед сохранением.

---

## 🏗 Архитектура (Pipeline Architecture)

Пайплайн состоит из двух слоев:

1.  **Слой парсинга (Golang):** Утилита `src/go-ast-parser` читает директорию `shared/api`, строит синтаксическое дерево и выгружает чистый JSON, содержащий только описания DTO (Structs, Enums, Aliases).
2.  **Слой генерации (Python):** Скрипт читает JSON, применяет правила маппинга типов (Go -> Rust), расставляет макросы `serde` (учитывая `omitempty`, зарезервированные слова Rust) и генерирует `.rs` файлы.

---

## ⚙️ Требования (Requirements)

Для запуска пайплайна требуются:
*   **Python 3.11+**
*   **Golang 1.22+**
*   **Rust (cargo)** (для этапа валидации сгенерированного кода)

---

## 🛠 Установка и настройка (Setup)

**1. Настройка виртуального окружения:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

**2. Сборка AST-парсера:**
```bash
cd src/go-ast-parser
go build -o parser
cd ../..
```

**3. Конфигурация путей (`.env`):**
Создайте файл `.env` в корне папки `generator` и укажите пути к исходникам Incus и целевой папке для сохранения DTO:

```bash
# Путь к склонированному репозиторию Incus (исходники)
INCUS_LOCAL_PATH=/home/dev/data/repos/incus

# Куда сохранять сгенерированные .rs файлы (например, в проект клиента)
OUTPUT_DIR=/home/dev/dto_converter/client/src/incus
```

---

## 🚀 Использование (Usage)

Чтобы запустить полный цикл (Парсинг -> Генерация -> Валидация -> Сохранение):

```bash
# Убедитесь, что .venv активирован
python -m src.main
```

### Ожидаемый вывод:
Скрипт проанализирует исходный код, выведет отчет по найденным сущностям, отфильтрует их по **Whitelist** (в `pipeline.py`), запустит `cargo check` и сохранит файлы.

```text
──────── Generation Report ────────
Total entities parsed: 254
Entities in Whitelist: 9
Structs generated: 4
Enums generated: 1
Aliases generated: 2
Output dir: /home/dev/dto_converter/client/src/incus
───────────────────────────────────

Validating all generated files...
Running cargo check...
✅ All generated files compile successfully!
💾 Saving 9 files to /home/dev/dto_converter/client/src/incus...
📦 Generated mod.rs
```

---

## 🎛 Настройка (Configuration)

### Whitelist (Белый список)
По умолчанию генератор создает только те структуры, которые реально используются в клиентском приложении (чтобы избежать лишнего мусора и предупреждений компилятора). 

Список нужных структур задается в переменной `TARGET_ENTITIES` в файле `src/pipeline.py`. 
Если вам нужны дополнительные API модели (например, для Storage или Profiles), просто добавьте их имя в этот список.

---

## 👨‍💻 Авторы
Разработано в рамках исследовательского проекта по автоматизации и межъязыковой синхронизации API моделей.