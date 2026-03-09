TYPE_MAP = {
    "string": "String",
    "bool": "bool",
    "int": "i64",
    "int8": "i8",
    "int16": "i16",
    "int32": "i32",
    "int64": "i64",
    "uint": "u64",
    "uint8": "u8",
    "uint16": "u16",
    "uint32": "u32",
    "uint64": "u64",
    "float32": "f32",
    "float64": "f64",
    "byte": "u8",
    "rune": "char",
    "time.Time": "chrono::DateTime<chrono::Utc>",
    "json.RawMessage": "serde_json::Value",
    "interface{}": "serde_json::Value",
    "any": "serde_json::Value",
}

PRIMITIVES = set(TYPE_MAP.keys())


def is_supported_type(go_type: str) -> bool:
    # В Stage 2 мы поддерживаем почти всё, но для чистоты оставим проверку
    return True


def map_go_type(go_type: str) -> str:
    go_type = go_type.strip()

    if go_type.startswith("[]"):
        inner = map_go_type(go_type[2:])
        return f"Vec<{inner}>"

    if go_type.startswith("map["):
        return "HashMap<String, String>"  # Упрощенно, пока так

    if go_type.startswith("*"):
        inner = map_go_type(go_type[1:])
        return f"Option<{inner}>"

    return TYPE_MAP.get(go_type, go_type)
