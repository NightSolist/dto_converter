TYPE_MAP = {
    "string": "String",
    "bool": "bool",
    "int": "i64",
    "int64": "i64",
    "uint64": "u64",
    "float64": "f64",
    "uint32": "u32",
    "uint16": "u16",
    "int32": "i32",
    "byte": "u8",
    "time.Time": "chrono::DateTime<chrono::Utc>",
    "json.RawMessage": "serde_json::Value",
    "interface{}": "serde_json::Value",
    "any": "serde_json::Value",
}

PRIMITIVES = set(TYPE_MAP.keys())


def is_supported_type(go_type: str) -> bool:
    return True  # В Stage 2 мы пробуем генерировать всё


def map_go_type(go_type: str) -> str:
    t = go_type.strip()
    
    if t.startswith("[]"):
        inner = map_go_type(t[2:])
        return f"Vec<{inner}>"

    if t.startswith("*"):
        inner = map_go_type(t[1:])
        return f"Option<{inner}>"

    if t.startswith("map["):
        # Парсим ключ и значение мапы с учетом вложенности.
        # Например: map[string]map[string]string
        bracket_level = 0
        for i, char in enumerate(t):
            if char == '[':
                bracket_level += 1
            elif char == ']':
                bracket_level -= 1

            # Когда мы нашли закрывающую скобку для ключа (и мы не внутри вложенных скобок)
            if bracket_level == 0 and i > 3:
                key_type = t[4:i]        # Извлекаем то, что между map[ и ]
                value_type = t[i+1:]     # Извлекаем остаток строки (значение)

                rust_key = map_go_type(key_type)
                rust_value = map_go_type(value_type)
                return f"HashMap<{rust_key}, {rust_value}>"

        # На случай, если парсинг ключа сломался
        return "HashMap<String, String>"

    return TYPE_MAP.get(t, t)