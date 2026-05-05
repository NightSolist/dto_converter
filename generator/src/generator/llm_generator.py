import re
from typing import Optional, Tuple

import requests

from src.parser.go_types import GoStruct


CODE_FENCE = "```"

SYSTEM_PROMPT = f"""
Ты — ИИ-ассистент, который преобразует структуры Go в идиоматичный Rust с поддержкой serde.

Правила трансформации:
- string -> String
- int -> i64
- bool -> bool
- []T -> Vec<T>
- map[string]string -> ConfigMap
- map[string]map[string]string -> DevicesMap
- time.Time -> chrono::DateTime<chrono::Utc>
- interface{{}} / any -> serde_json::Value

Правила генерации:
1. Всегда добавляй:
   #[derive(Debug, Clone, Serialize, Deserialize, Default)]

2. Всегда подключай serde:
   use serde::{{Serialize, Deserialize}};

3. Если используется ConfigMap, добавь:
   use crate::incus::ConfigMap;

4. Если используется DevicesMap, добавь:
   use crate::incus::DevicesMap;

5. Если поле имеет тег json:"name", используй:
   #[serde(rename = "name")]

6. Если поле имеет omitempty:
   - оберни тип в Option<T>
   - добавь #[serde(skip_serializing_if = "Option::is_none")]

7. Если структура встроенная через yaml:",inline":
   используй #[serde(flatten)]

8. Если имя поля является ключевым словом Rust (например type),
   используй r#type.

ВАЖНО:
- ConfigMap и DevicesMap уже существуют в crate::incus
- НЕ объявляй их заново внутри файла
- НЕ создавай локальные type/struct/enum ConfigMap
- НЕ создавай локальные type/struct/enum DevicesMap
- Просто импортируй их из crate::incus

Пример правильного результата:

{CODE_FENCE}rust
use serde::{{Serialize, Deserialize}};
use crate::incus::ConfigMap;
use crate::incus::DevicesMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ProfilePut {{
    pub config: ConfigMap,
    pub description: String,
    pub devices: DevicesMap,
}}
{CODE_FENCE}

Верни только готовый Rust-код внутри блока {CODE_FENCE}rust ... {CODE_FENCE}.
Без пояснений, комментариев и лишнего текста.
"""


class LLMGenerator:
    def __init__(
        self,
        ollama_url: str = "http://127.0.0.1:11434/api/chat",
        model: str = "qwen2.5-coder:1.5b",
        timeout_seconds: int = 120,
        max_retries: int = 3,
    ):
        self.ollama_url = ollama_url
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    def generate(
        self,
        go_struct: GoStruct,
        validator,
        test_env_files: dict[str, str],
        raw_go_code: str,
    ) -> Tuple[bool, Optional[str], str]:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Преобразуй этот Go-код в Rust:\n"
                    f"{CODE_FENCE}go\n{raw_go_code}\n{CODE_FENCE}"
                ),
            },
        ]

        filename = f"{self._camel_to_snake(go_struct.name)}.rs"

        last_error_normalized = None
        repeated_same_error_count = 0

        for attempt in range(1, self.max_retries + 1):
            print(f"      🤖 [LLM] Попытка {attempt}/{self.max_retries} для {go_struct.name}...")

            try:
                response = requests.post(
                    self.ollama_url,
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                        "options": {
                            "temperature": 0.1,
                        },
                    },
                    timeout=self.timeout_seconds,
                )
                response.raise_for_status()
            except requests.RequestException as e:
                return False, None, f"Ошибка API Ollama: {e}"

            content = response.json().get("message", {}).get("content", "")
            rust_code = self._extract_rust_code(content)

            if not rust_code:
                error_msg = f"Модель не вернула блок {CODE_FENCE}rust{CODE_FENCE}."
                print(f"      ⚠️ [LLM] Ошибка (попытка {attempt}): {error_msg}")
                messages.append({"role": "assistant", "content": content})
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            f"Верни только Rust-код внутри блока "
                            f"{CODE_FENCE}rust ... {CODE_FENCE} без пояснений."
                        ),
                    }
                )
                continue

            rust_code = self._ensure_imports(rust_code)

            forbidden_error = self._check_forbidden_local_types(rust_code)
            if forbidden_error:
                print(f"      ⚠️ [LLM] Ошибка (попытка {attempt}): {forbidden_error}")
                messages.append(
                    {
                        "role": "assistant",
                        "content": f"{CODE_FENCE}rust\n{rust_code}\n{CODE_FENCE}",
                    }
                )
                messages.append(
                    {
                        "role": "user",
                        "content": forbidden_error + "\nИсправь код и верни полный правильный файл.",
                    }
                )
                continue

            val_res = validator.validate_single(filename, rust_code, test_env_files)

            if val_res.passed:
                return True, rust_code, f"Успех с попытки {attempt}"

            error_msg = val_res.error_message or "Неизвестная ошибка компиляции"
            normalized_error = self._normalize_error(error_msg)

            print(f"      ⚠️ [LLM] Ошибка (попытка {attempt}): {error_msg}")

            if normalized_error == last_error_normalized:
                repeated_same_error_count += 1
            else:
                repeated_same_error_count = 0

            last_error_normalized = normalized_error

            if repeated_same_error_count >= 1:
                return False, None, f"Повторяющаяся ошибка LLM: {error_msg}"

            messages.append(
                {
                    "role": "assistant",
                    "content": f"{CODE_FENCE}rust\n{rust_code}\n{CODE_FENCE}",
                }
            )
            messages.append(
                {
                    "role": "user",
                    "content": (
                        "Твой код не компилируется. Ошибка cargo check:\n"
                        f"{error_msg}\n"
                        "Исправь ошибку. "
                        "Не объявляй локально ConfigMap и DevicesMap. "
                        "Если они нужны, просто импортируй их из crate::incus."
                    ),
                }
            )

        return False, None, "Исчерпан лимит попыток LLM"

    def _extract_rust_code(self, text: str) -> Optional[str]:
        pattern = re.escape(CODE_FENCE) + r"rust\s*(.*?)\s*" + re.escape(CODE_FENCE)
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def _ensure_imports(self, rust_code: str) -> str:
        """
        Автоматически добавляет недостающие импорты для ConfigMap и DevicesMap,
        если модель использовала тип, но забыла сделать use.
        """
        needs_config_map = (
            "ConfigMap" in rust_code
            and "use crate::incus::ConfigMap;" not in rust_code
        )
        needs_devices_map = (
            "DevicesMap" in rust_code
            and "use crate::incus::DevicesMap;" not in rust_code
        )

        if not needs_config_map and not needs_devices_map:
            return rust_code

        lines = rust_code.splitlines()
        import_lines = []

        if needs_config_map:
            import_lines.append("use crate::incus::ConfigMap;")
        if needs_devices_map:
            import_lines.append("use crate::incus::DevicesMap;")

        insert_pos = 0

        for i, line in enumerate(lines):
            stripped = line.strip()

            if stripped.startswith("use "):
                insert_pos = i + 1
            elif stripped.startswith("#[derive"):
                if insert_pos == 0:
                    insert_pos = i
                break

        for offset, import_line in enumerate(import_lines):
            if import_line not in lines:
                lines.insert(insert_pos + offset, import_line)

        return "\n".join(lines)

    def _check_forbidden_local_types(self, rust_code: str) -> Optional[str]:
        forbidden_patterns = [
            r"\b(pub\s+)?type\s+ConfigMap\b",
            r"\b(pub\s+)?struct\s+ConfigMap\b",
            r"\b(pub\s+)?enum\s+ConfigMap\b",
            r"\b(pub\s+)?type\s+DevicesMap\b",
            r"\b(pub\s+)?struct\s+DevicesMap\b",
            r"\b(pub\s+)?enum\s+DevicesMap\b",
        ]

        for pattern in forbidden_patterns:
            if re.search(pattern, rust_code):
                return (
                    "Запрещено объявлять ConfigMap или DevicesMap внутри "
                    "сгенерированного файла. Эти типы уже существуют в crate::incus "
                    "и должны только импортироваться."
                )

        return None

    def _normalize_error(self, error_msg: str) -> str:
        normalized = error_msg.strip().lower()
        normalized = re.sub(r"\s+", " ", normalized)
        return normalized

    def _camel_to_snake(self, name: str) -> str:
        s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()