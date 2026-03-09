import re
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


class RustGenerator:
    def __init__(self, known_types: set[str] = None):
        self.known_types = known_types or set()

    def generate_struct(self, go_struct: GoStruct) -> str:
        field_lines = []
        imports = set()
        
        needs_hashmap = False
        needs_serde_json = False

        for field in go_struct.fields:
            rust_type = map_go_type(field.go_type)
            field_name = field.name.lower()

            if re.search(r'\bHashMap\b', rust_type):
                needs_hashmap = True
            if re.search(r'\bserde_json::Value\b', rust_type):
                needs_serde_json = True

            types_in_field = self._extract_all_types(rust_type)
            for t in types_in_field:
                if t in self.known_types and t != go_struct.name:
                    imports.add(f"use super::{t.lower()}::{t};")

            rename_attr = ""
            if field_name in RUST_KEYWORDS:
                rename_attr = f'    #[serde(rename = "{field_name}")]'
                field_name = f"r#{field_name}"

            if field.tag.omitempty and not rust_type.startswith("Option<"):
                rust_type = f"Option<{rust_type}>"
                if rename_attr:
                    field_lines.append(rename_attr)
                field_lines.append('    #[serde(skip_serializing_if = "Option::is_none")]')
            else:
                if rename_attr:
                    field_lines.append(rename_attr)

            field_lines.append(f"    pub {field_name}: {rust_type},")
            field_lines.append("")

        lines = []
        lines.append("// Auto-generated. Do not edit.\n")
        lines.append("use serde::{Serialize, Deserialize};")
        
        if needs_hashmap:
            lines.append("use std::collections::HashMap;")
        if needs_serde_json:
            lines.append("use serde_json;")

        for imp in sorted(imports):
            lines.append(imp)

        lines.append("")
        lines.append("#[derive(Debug, Clone, Serialize, Deserialize, Default)]")
        lines.append(f"pub struct {go_struct.name} {{")
        lines.extend(field_lines)
        lines.append("}")

        return "\n".join(lines)

    def generate_enum(self, go_enum: GoEnum) -> str:
        lines = []
        lines.append("// Auto-generated. Do not edit.\n")
        lines.append("use serde::{Serialize, Deserialize};")
        lines.append("")
        
        repr_type = "i32" if "int" in go_enum.base_type else "String"
        
        lines.append("#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, Default)]")
        if repr_type == "i32":
             lines.append("#[repr(i32)]")
             
        lines.append(f"pub enum {go_enum.name} {{")
        
        for i, (name, val) in enumerate(go_enum.values):
            default_attr = "    #[default]" if i == 0 else ""
            clean_val = val.strip('"')
            
            if repr_type == "i32":
                if default_attr: lines.append(default_attr)
                lines.append(f"    {name} = {val},")
            else:
                if default_attr: lines.append(default_attr)
                if clean_val != "":
                    lines.append(f'    #[serde(rename = "{clean_val}")]')
                else:
                    lines.append('    #[serde(rename = "")]')
                
                lines.append(f"    {name},")
        lines.append("}")
        return "\n".join(lines)

    def generate_alias(self, go_alias: GoAlias) -> str:
        lines = []
        lines.append("// Auto-generated. Do not edit.\n")
        
        rust_type = map_go_type(go_alias.target_type)
        
        if re.search(r'\bHashMap\b', rust_type):
            lines.append("use std::collections::HashMap;")
        if re.search(r'\bserde_json::Value\b', rust_type):
            lines.append("use serde_json;")

        types_in_field = self._extract_all_types(rust_type)
        for t in types_in_field:
            if t in self.known_types and t != go_alias.name:
                lines.append(f"use super::{t.lower()}::{t};")
            
        lines.append("")
        lines.append(f"pub type {go_alias.name} = {rust_type};")
        return "\n".join(lines)

    def _extract_all_types(self, rust_type: str) -> list[str]:
        clean_str = rust_type.replace("<", " ").replace(">", " ").replace(",", " ")
        words = clean_str.split()
        return [w for w in words if w]