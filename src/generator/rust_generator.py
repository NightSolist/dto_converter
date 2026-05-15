import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .type_mapping import map_go_type
from src.parser.go_types import GoAlias, GoEnum, GoStruct

RUST_KEYWORDS = {
    "type", "move", "ref", "self", "super", "crate",
    "fn", "mod", "pub", "use", "let", "mut", "const",
    "static", "struct", "enum", "trait", "impl", "for",
    "loop", "while", "if", "else", "match", "return",
    "break", "continue", "as", "in", "where", "async",
    "await", "dyn", "abstract", "box", "do", "final",
    "macro", "override", "priv", "typeof", "unsized",
    "virtual", "yield", "try", "union",
}

# Типы с кастомной десериализацией —
# генерируются через специальный шаблон
SPECIAL_ALIASES = {"ConfigMap", "DevicesMap"}


def camel_to_snake(name: str) -> str:
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


class RustGenerator:
    def __init__(self, known_types: set[str] = None):
        self.known_types = known_types or set()

        templates_dir = (
            Path(__file__).parent.parent.parent / "templates"
        )
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate_struct(self, go_struct: GoStruct) -> str:
        needs_hashmap = False
        needs_serde_json = False
        needs_chrono = False
        needs_config_map = False
        needs_devices_map = False
        needs_config_map_deser = False
        needs_devices_map_deser = False
        imports = set()
        fields_data = []

        # Embedded структуры → #[serde(flatten)]
        for emb_name in go_struct.embedded:
            clean_name = emb_name.lstrip("*").split(".")[-1]
            field_name = camel_to_snake(clean_name)

            if (
                clean_name in self.known_types
                and clean_name not in SPECIAL_ALIASES
            ):
                imports.add(clean_name)

            fields_data.append({
                "name": field_name,
                "rust_type": clean_name,
                "serde_args": ["flatten"],
            })

        # Обычные поля
        for field in go_struct.fields:
            rust_type = map_go_type(field.go_type)

            json_name = (
                field.tag.json_name
                if field.tag.json_name is not None
                else field.name
            )
            rust_field_name = camel_to_snake(field.name)

            rename = None

            if rust_field_name in RUST_KEYWORDS:
                rename = json_name
                rust_field_name = f"r#{rust_field_name}"
            elif "-" in json_name:
                rename = json_name
                rust_field_name = json_name.replace("-", "_")
            elif (
                json_name != rust_field_name
                and json_name != field.name
            ):
                rename = json_name

            # Проверка зависимостей
            if "HashMap<" in rust_type:
                needs_hashmap = True
            if "serde_json::Value" in rust_type:
                needs_serde_json = True
            if "chrono::DateTime" in rust_type:
                needs_chrono = True
            if "ConfigMap" in rust_type:
                needs_config_map = True
            if "DevicesMap" in rust_type:
                needs_devices_map = True

            # Импорты для known типов
            for t in self._extract_type_names(rust_type):
                if (
                    t in self.known_types
                    and t != go_struct.name
                    and t not in SPECIAL_ALIASES
                ):
                    imports.add(t)

            # omitempty
            is_option = False
            if field.tag.omitempty:
                if not rust_type.startswith("Option<"):
                    rust_type = f"Option<{rust_type}>"
                is_option = True
            elif rust_type.startswith("Option<"):
                is_option = True

            # Сборка serde-аргументов
            serde_args = []

            if rename:
                serde_args.append(f'rename = "{rename}"')

            # Кастомные десериализаторы
            if rust_type == "ConfigMap":
                needs_config_map_deser = True
                serde_args.append(
                    'deserialize_with = "deserialize_config_map"'
                )
            elif rust_type == "Option<ConfigMap>":
                needs_config_map_deser = True
                serde_args.append("default")
                serde_args.append(
                    'deserialize_with = "deserialize_option_config_map"'
                )
            elif rust_type == "DevicesMap":
                needs_devices_map_deser = True
                serde_args.append(
                    'deserialize_with = "deserialize_devices_map"'
                )
            elif rust_type == "Option<DevicesMap>":
                needs_devices_map_deser = True
                serde_args.append("default")
                serde_args.append(
                    'deserialize_with = "deserialize_option_devices_map"'
                )

            if is_option:
                serde_args.append(
                    'skip_serializing_if = "Option::is_none"'
                )

            fields_data.append({
                "name": rust_field_name,
                "rust_type": rust_type,
                "serde_args": serde_args,
            })

        template = self.env.get_template("struct.rs.j2")
        return template.render(
            name=go_struct.name,
            fields=fields_data,
            needs_hashmap=needs_hashmap,
            needs_serde_json=needs_serde_json,
            needs_chrono=needs_chrono,
            needs_config_map=needs_config_map,
            needs_devices_map=needs_devices_map,
            needs_config_map_deser=needs_config_map_deser,
            needs_devices_map_deser=needs_devices_map_deser,
            imports=sorted(imports),
        )

    def generate_enum(self, go_enum: GoEnum) -> str:
        repr_type = (
            "i32" if "int" in go_enum.base_type else "String"
        )
        variants_data = []

        for i, (name, val) in enumerate(go_enum.values):
            clean_val = val.strip('"')
            is_default = (i == 0)
            variants_data.append({
                "name": name,
                "is_default": is_default,
                "value": val if repr_type == "i32" else None,
                "rename": (
                    clean_val if repr_type != "i32" else None
                ),
            })

        template = self.env.get_template("enum.rs.j2")
        return template.render(
            name=go_enum.name,
            repr_type=repr_type,
            variants=variants_data,
        )

    def generate_alias(self, go_alias: GoAlias) -> str:
        """
        ConfigMap и DevicesMap генерируются через
        специальные шаблоны с кастомной десериализацией.
        Остальные алиасы — через alias.rs.j2.
        """
        if go_alias.name == "ConfigMap":
            template = self.env.get_template("config_map.rs.j2")
            return template.render()

        if go_alias.name == "DevicesMap":
            template = self.env.get_template("devices_map.rs.j2")
            return template.render()

        rust_type = map_go_type(go_alias.target_type)

        needs_hashmap = "HashMap<" in rust_type
        needs_serde_json = "serde_json::Value" in rust_type
        imports = set()

        for t in self._extract_type_names(rust_type):
            if (
                t in self.known_types
                and t != go_alias.name
                and t not in SPECIAL_ALIASES
            ):
                imports.add(t)

        template = self.env.get_template("alias.rs.j2")
        return template.render(
            name=go_alias.name,
            rust_type=rust_type,
            needs_hashmap=needs_hashmap,
            needs_serde_json=needs_serde_json,
            imports=sorted(imports),
        )

    def generate_mod_file(
        self,
        generated_entities: list[tuple[str, str]],
    ) -> str:
        modules = sorted(list(
            set(mod for _, mod in generated_entities)
        ))
        exports = sorted(
            generated_entities, key=lambda x: x[0]
        )
        template = self.env.get_template("mod.rs.j2")
        return template.render(
            modules=modules,
            exports=exports,
        )

    def _extract_type_names(self, rust_type: str) -> list[str]:
        clean = (
            rust_type
            .replace("<", " ")
            .replace(">", " ")
            .replace(",", " ")
        )
        return [
            w for w in clean.split()
            if w and w[0].isupper()
        ]