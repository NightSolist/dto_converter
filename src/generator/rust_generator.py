import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .type_mapping import map_go_type
from src.parser.go_types import GoStruct, GoEnum, GoAlias

RUST_KEYWORDS = {
    "type", "move", "ref", "self", "super", "crate",
    "fn", "mod", "pub", "use", "let", "mut", "const",
    "static", "struct", "enum", "trait", "impl", "for",
    "loop", "while", "if", "else", "match", "return",
    "break", "continue", "as", "in", "where", "async",
    "await", "dyn", "abstract", "box", "do", "final",
    "macro", "override", "priv", "typeof", "unsized",
    "virtual", "yield", "try", "union"
}

MANUAL_INCUS_TYPES = {"ConfigMap", "DevicesMap"}


class RustGenerator:
    def __init__(self, known_types: set[str] = None):
        self.known_types = known_types or set()

        templates_dir = Path(__file__).parent.parent.parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def generate_struct(self, go_struct: GoStruct) -> str:
        needs_hashmap = False
        needs_serde_json = False
        needs_config_map = False
        needs_devices_map = False
        imports = set()
        fields_data = []

        for field in go_struct.fields:
            rust_type = map_go_type(field.go_type)
            field_name = field.name.lower()

            if re.search(r"\bHashMap\b", rust_type):
                needs_hashmap = True
            if re.search(r"\bserde_json::Value\b", rust_type):
                needs_serde_json = True
            if re.search(r"\bConfigMap\b", rust_type):
                needs_config_map = True
            if re.search(r"\bDevicesMap\b", rust_type):
                needs_devices_map = True

            # Сбор импортов для известных типов,
            # но ручные типы ConfigMap / DevicesMap исключаем:
            # они импортируются отдельно через needs_config_map / needs_devices_map.
            types_in_field = self._extract_all_types(rust_type)
            for t in types_in_field:
                if (
                    t in self.known_types
                    and t != go_struct.name
                    and t not in MANUAL_INCUS_TYPES
                ):
                    imports.add(t)

            rename = None
            if field_name in RUST_KEYWORDS:
                rename = field_name
                field_name = f"r#{field_name}"

            skip_none = False
            if field.tag.omitempty and not rust_type.startswith("Option<"):
                rust_type = f"Option<{rust_type}>"
                skip_none = True

            fields_data.append({
                "name": field_name,
                "rust_type": rust_type,
                "rename": rename,
                "skip_none": skip_none
            })

        template = self.env.get_template("struct.rs.j2")
        return template.render(
            name=go_struct.name,
            fields=fields_data,
            needs_hashmap=needs_hashmap,
            needs_serde_json=needs_serde_json,
            needs_config_map=needs_config_map,
            needs_devices_map=needs_devices_map,
            imports=sorted(imports)
        )

    def generate_enum(self, go_enum: GoEnum) -> str:
        repr_type = "i32" if "int" in go_enum.base_type else "String"
        variants_data = []

        for i, (name, val) in enumerate(go_enum.values):
            clean_val = val.strip('"')
            is_default = (i == 0)

            variant = {
                "name": name,
                "is_default": is_default,
                "value": val if repr_type == "i32" else None,
                "rename": clean_val if repr_type != "i32" else None
            }
            variants_data.append(variant)

        template = self.env.get_template("enum.rs.j2")
        return template.render(
            name=go_enum.name,
            repr_type=repr_type,
            variants=variants_data
        )

    def generate_alias(self, go_alias: GoAlias) -> str:
        lines = ["// Auto-generated. Do not edit.\n"]
        rust_type = map_go_type(go_alias.target_type)

        if re.search(r"\bHashMap\b", rust_type):
            lines.append("use std::collections::HashMap;")
        if re.search(r"\bserde_json::Value\b", rust_type):
            lines.append("use serde_json;")

        if re.search(r"\bConfigMap\b", rust_type):
            lines.append("use crate::incus::ConfigMap;")
        if re.search(r"\bDevicesMap\b", rust_type):
            lines.append("use crate::incus::DevicesMap;")

        types_in_field = self._extract_all_types(rust_type)
        for t in types_in_field:
            if (
                t in self.known_types
                and t != go_alias.name
                and t not in MANUAL_INCUS_TYPES
            ):
                lines.append(f"use crate::incus::{t};")

        lines.append(f"\npub type {go_alias.name} = {rust_type};")
        return "\n".join(lines)

    def generate_mod_file(self, generated_entities: list[tuple[str, str]]) -> str:
        modules = sorted(list(set(mod for _, mod in generated_entities)))
        exports = sorted(generated_entities, key=lambda x: x[0])

        template = self.env.get_template("mod.rs.j2")
        return template.render(modules=modules, exports=exports)

    def _extract_all_types(self, rust_type: str) -> list[str]:
        clean_str = (
            rust_type
            .replace("<", " ")
            .replace(">", " ")
            .replace(",", " ")
        )
        words = clean_str.split()
        return [w for w in words if w]