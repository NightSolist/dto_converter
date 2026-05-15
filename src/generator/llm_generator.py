import re
from typing import Optional, Tuple

import requests


CODE_FENCE = "```"

SYSTEM_PROMPT = f"""
Ты — ИИ-ассистент, который исправляет Rust-код,
автоматически сгенерированный шаблонным генератором
из Go-моделей Incus.

ТВОЯ ЗАДАЧА:
- НЕ переписывать код с нуля.
- Минимально исправить шаблонный Rust-код,
  чтобы он компилировался.
- Сохранять структуру, стиль и имена,
  заданные шаблоном.
- Менять только то, что вызывает ошибку.

ПРАВИЛА СИНХРОНИЗАЦИИ Go -> Rust:
- string -> String
- int -> i64  (НИКОГДА не i32 для Go int)
- int64 -> i64
- int32 -> i32
- uint -> u64
- uint64 -> u64
- uint32 -> u32
- float64 -> f64
- bool -> bool
- []T -> Vec<T>
- *T -> Option<T>
- map[string]string -> ConfigMap
- map[string]map[string]string -> DevicesMap
- time.Time -> chrono::DateTime<chrono::Utc>
- interface{{}} / any -> serde_json::Value

ПРАВИЛА serde:
- json:"name" -> #[serde(rename = "name")]
  только если JSON-имя отличается от snake_case поля
- omitempty -> Option<T> +
  #[serde(skip_serializing_if = "Option::is_none")]
- yaml:",inline" -> #[serde(flatten)]
- поле type -> r#type + #[serde(rename = "type")]
- JSON-имя с дефисом (base-image) ->
  поле base_image + #[serde(rename = "base-image")]

ПРАВИЛА ПО ConfigMap / DevicesMap:
- Эти типы уже существуют в crate::incus.
- Для них также существуют helper-функции:
    deserialize_config_map
    deserialize_option_config_map
    deserialize_devices_map
    deserialize_option_devices_map
- НЕ объявляй ConfigMap и DevicesMap заново.
- НЕ создавай локальные type/struct/enum с такими именами.
- Просто добавь нужный импорт если он отсутствует.

ФОРМАТ ОТВЕТА:
Верни ТОЛЬКО исправленный Rust-код внутри блока:
{CODE_FENCE}rust
...
{CODE_FENCE}
Без пояснений и комментариев.
"""

FEW_SHOT_EXAMPLES = [
    {
        "user": (
            "Ниже Go-код, шаблонный Rust-код и ошибка компиляции.\n\n"
            "Go-код:\n"
            f"{CODE_FENCE}go\n"
            "type NetworkPut struct {\n"
            '    Config      ConfigMap `json:"config" yaml:"config"`\n'
            '    Description string    `json:"description" yaml:"description"`\n'
            "}\n"
            f"{CODE_FENCE}\n\n"
            "Шаблонный Rust-код:\n"
            f"{CODE_FENCE}rust\n"
            "use serde::{Serialize, Deserialize};\n"
            "\n"
            "#[derive(Debug, Clone, Serialize, Deserialize, Default)]\n"
            "pub struct NetworkPut {\n"
            "    pub config: ConfigMap,\n"
            "    pub description: String,\n"
            "}\n"
            f"{CODE_FENCE}\n\n"
            "Ошибка компиляции:\n"
            f"{CODE_FENCE}\n"
            "cannot find type `ConfigMap` in this scope\n"
            f"{CODE_FENCE}\n\n"
            "Исправь шаблонный Rust-код минимально."
        ),
        "assistant": (
            f"{CODE_FENCE}rust\n"
            "use serde::{Serialize, Deserialize};\n"
            "use crate::incus::ConfigMap;\n"
            "use crate::incus::config_map::deserialize_config_map;\n"
            "\n"
            "#[derive(Debug, Clone, Serialize, Deserialize, Default)]\n"
            "pub struct NetworkPut {\n"
            "    #[serde(deserialize_with = \"deserialize_config_map\")]\n"
            "    pub config: ConfigMap,\n"
            "    pub description: String,\n"
            "}\n"
            f"{CODE_FENCE}"
        ),
    },
    {
        "user": (
            "Ниже Go-код, шаблонный Rust-код и ошибка компиляции.\n\n"
            "Go-код:\n"
            f"{CODE_FENCE}go\n"
            "type InstanceSource struct {\n"
            '    Type      string `json:"type" yaml:"type"`\n'
            '    BaseImage string `json:"base-image,omitempty"`\n'
            '    Live      bool   `json:"live,omitempty"`\n'
            "}\n"
            f"{CODE_FENCE}\n\n"
            "Шаблонный Rust-код:\n"
            f"{CODE_FENCE}rust\n"
            "use serde::{Serialize, Deserialize};\n"
            "\n"
            "#[derive(Debug, Clone, Serialize, Deserialize, Default)]\n"
            "pub struct InstanceSource {\n"
            "    #[serde(rename = \"type\")]\n"
            "    pub r#type: String,\n"
            "    #[serde(skip_serializing_if = \"Option::is_none\")]\n"
            "    pub baseimage: Option<String>,\n"
            "    #[serde(skip_serializing_if = \"Option::is_none\")]\n"
            "    pub live: Option<bool>,\n"
            "}\n"
            f"{CODE_FENCE}\n\n"
            "Ошибка компиляции:\n"
            f"{CODE_FENCE}\n"
            "поле baseimage должно сериализоваться как base-image\n"
            f"{CODE_FENCE}\n\n"
            "Исправь шаблонный Rust-код минимально."
        ),
        "assistant": (
            f"{CODE_FENCE}rust\n"
            "use serde::{Serialize, Deserialize};\n"
            "\n"
            "#[derive(Debug, Clone, Serialize, Deserialize, Default)]\n"
            "pub struct InstanceSource {\n"
            "    #[serde(rename = \"type\")]\n"
            "    pub r#type: String,\n"
            "    #[serde(rename = \"base-image\","
            " skip_serializing_if = \"Option::is_none\")]\n"
            "    pub base_image: Option<String>,\n"
            "    #[serde(skip_serializing_if = \"Option::is_none\")]\n"
            "    pub live: Option<bool>,\n"
            "}\n"
            f"{CODE_FENCE}"
        ),
    },
]


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

    def repair(
        self,
        entity_name: str,
        raw_go_code: str,
        template_rust_code: str,
        initial_error: str,
        validator,
        test_env_files: dict[str, str],
        filename: str,
    ) -> Tuple[bool, Optional[str], str]:
        """
        Исправляет шаблонно сгенерированный Rust-код.
        Получает на вход шаблонный результат и ошибку компиляции.
        Возвращает (success, rust_code | None, info).
        """
        last_error_normalized = None
        repeated_same_error_count = 0
        current_rust_code = template_rust_code
        error_feedback = initial_error

        for attempt in range(1, self.max_retries + 1):
            print(
                f"      🤖 [LLM repair] "
                f"Попытка {attempt}/{self.max_retries} "
                f"для {entity_name}..."
            )

            messages = self._build_repair_messages(
                raw_go_code=raw_go_code,
                template_rust_code=current_rust_code,
                error_feedback=error_feedback,
            )

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

            content = (
                response.json()
                .get("message", {})
                .get("content", "")
            )
            rust_code = self._extract_rust_code(content)

            if not rust_code:
                error_feedback = (
                    f"Модель не вернула блок "
                    f"{CODE_FENCE}rust{CODE_FENCE}. "
                    f"Верни только исправленный Rust-код "
                    f"внутри блока "
                    f"{CODE_FENCE}rust ... {CODE_FENCE}."
                )
                print(
                    f"      ⚠️ [LLM repair] "
                    f"Нет блока rust (попытка {attempt})"
                )
                continue

            rust_code = self._split_use_statements(rust_code)
            rust_code = self._ensure_pub_fields(rust_code)
            rust_code = self._fix_int_types(rust_code, raw_go_code)

            val_res = validator.validate_single(
                filename, rust_code, test_env_files
            )

            if val_res.passed:
                return True, rust_code, f"Успех с попытки {attempt}"

            error_msg = (
                val_res.error_message
                or "Неизвестная ошибка компиляции"
            )
            normalized_error = self._normalize_error(error_msg)

            print(
                f"      ⚠️ [LLM repair] "
                f"Ошибка (попытка {attempt}): "
                f"{error_msg[:120]}..."
            )

            if normalized_error == last_error_normalized:
                repeated_same_error_count += 1
            else:
                repeated_same_error_count = 0

            last_error_normalized = normalized_error

            if repeated_same_error_count >= 1:
                return (
                    False,
                    None,
                    f"Повторяющаяся ошибка: {error_msg}",
                )

            current_rust_code = rust_code
            error_feedback = error_msg

        return False, None, "Исчерпан лимит попыток LLM repair"

    def _build_repair_messages(
        self,
        raw_go_code: str,
        template_rust_code: str,
        error_feedback: str,
    ) -> list[dict]:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]

        for example in FEW_SHOT_EXAMPLES:
            messages.append({
                "role": "user",
                "content": example["user"].strip(),
            })
            messages.append({
                "role": "assistant",
                "content": example["assistant"].strip(),
            })

        user_prompt = (
            "Ниже Go-код, шаблонно сгенерированный Rust-код "
            "и ошибка компиляции.\n\n"
            f"Go-код:\n"
            f"{CODE_FENCE}go\n{raw_go_code}\n{CODE_FENCE}\n\n"
            f"Шаблонный/текущий Rust-код:\n"
            f"{CODE_FENCE}rust\n{template_rust_code}\n{CODE_FENCE}\n\n"
            f"Ошибка компиляции:\n"
            f"{CODE_FENCE}\n{error_feedback}\n{CODE_FENCE}\n\n"
            "Исправь Rust-код минимально.\n"
            "Не переписывай файл заново.\n"
            "Сохрани стиль шаблонной генерации.\n"
            "Верни только исправленный Rust-код."
        )

        messages.append({
            "role": "user",
            "content": user_prompt.strip(),
        })
        return messages

    def _extract_rust_code(self, text: str) -> Optional[str]:
        pattern = (
            re.escape(CODE_FENCE)
            + r"rust\s*(.*?)\s*"
            + re.escape(CODE_FENCE)
        )
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def _split_use_statements(self, rust_code: str) -> str:
        lines = rust_code.splitlines()
        result = []
        for line in lines:
            if line.count("use ") > 1:
                parts = [
                    p.strip()
                    for p in line.split(";")
                    if p.strip()
                ]
                for part in parts:
                    if not part.endswith(";"):
                        part += ";"
                    result.append(part)
            else:
                result.append(line)
        return "\n".join(result)

    def _ensure_pub_fields(self, rust_code: str) -> str:
        lines = rust_code.splitlines()
        result = []
        inside_struct = False
        brace_depth = 0

        for line in lines:
            stripped = line.strip()

            if re.match(r'^\s*pub\s+struct\s+\w+', line):
                inside_struct = True
                result.append(line)
                brace_depth += line.count("{") - line.count("}")
                continue

            if inside_struct:
                brace_depth += line.count("{") - line.count("}")

                is_attr = stripped.startswith("#[")
                is_close = stripped.startswith("}")
                is_blank = not stripped
                already_pub = stripped.startswith("pub ")
                looks_like_field = bool(
                    re.match(r'^[a-zA-Z_][\w#]*\s*:', stripped)
                )

                if (
                    not is_attr
                    and not is_close
                    and not is_blank
                    and not already_pub
                    and looks_like_field
                ):
                    indent = line[: len(line) - len(line.lstrip())]
                    line = f"{indent}pub {stripped}"

                if brace_depth <= 0:
                    inside_struct = False

            result.append(line)

        return "\n".join(result)

    def _fix_int_types(
        self, rust_code: str, raw_go_code: str
    ) -> str:
        go_int_fields = set(
            re.findall(r'\b(\w+)\s+int\b(?!\d)', raw_go_code)
        )

        if not go_int_fields:
            return rust_code

        lines = rust_code.splitlines()
        result = []

        for line in lines:
            for field in go_int_fields:
                snake_field = self._camel_to_snake(field)
                if snake_field in line.lower() and "i32" in line:
                    line = line.replace("i32", "i64")
                    break
            result.append(line)

        return "\n".join(result)

    def _normalize_error(self, error_msg: str) -> str:
        normalized = error_msg.strip().lower()
        normalized = re.sub(r"\s+", " ", normalized)
        return normalized

    def _camel_to_snake(self, name: str) -> str:
        s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()