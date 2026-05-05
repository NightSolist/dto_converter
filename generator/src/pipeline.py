import os
import re
from pathlib import Path

from src.config import Config
from src.dispatcher import Dispatcher
from src.generator.llm_generator import LLMGenerator
from src.generator.rust_generator import RustGenerator
from src.parser.factory import ParserFactory
from src.validation.validator import RustValidator


# Включает режим прототипа:
# - фильтрация только по whitelist прототипа
# - вывод по умолчанию идет в prototype_output_dir
PROTOTYPE_MODE = True

# Типы, которые пишутся вручную и не должны перезаписываться генератором
MANUAL_TYPES = {"ConfigMap", "DevicesMap"}

# Если структура содержит такие типы, она попадает в категорию "сложных"
TYPES_REQUIRING_LLM = {"ConfigMap", "DevicesMap"}

# Белый список структур, входящих в текущий прототип.
# StoragePoolState временно исключён, так как тянет внешнюю зависимость
# ResourcesStoragePoolSpace и ломает "простой" subset прототипа.
PROTOTYPE_STRUCT_WHITELIST = {
    # certificate.go
    "Certificate",
    "CertificatePut",
    "CertificatesPost",
    "CertificateAddToken",

    # profile.go
    "Profile",
    "ProfilePut",
    "ProfilesPost",

    # project.go
    "Project",
    "ProjectPut",
    "ProjectsPost",

    # storage_pool.go
    "StoragePool",
    "StoragePoolPut",
    "StoragePoolsPost",

    # network.go
    "Network",
    "NetworkPut",
    "NetworksPost",

    # cluster.go
    "ClusterMember",
    "ClusterMemberPut",

    # operation.go
    "Operation",

    # instance_state.go
    "InstanceStatePut",

    # instance.go (только разрешённая часть текущего этапа)
    "InstancePut",
}

# Явно разрешённые enum-типы прототипа.
# Если InstanceType в конкретной версии API окажется enum, он останется в прототипе.
PROTOTYPE_ENUM_WHITELIST = {
    "InstanceType",
}

# Явно разрешённые alias-типы прототипа.
# Если InstanceType в конкретной версии API окажется alias, он останется в прототипе.
PROTOTYPE_ALIAS_WHITELIST = {
    "InstanceType",
}

# Текущий подтверждённый стабильный whitelist для LLM.
# Все 5 структур уже проходили через LLM с первой попытки.
LLM_TEST_WHITELIST = {
    "ProfilePut",
    "ProfilesPost",
    "InstancePut",
    "NetworkPut",
    "StoragePoolPut",
}


def camel_to_snake(name: str) -> str:
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


class Pipeline:
    def __init__(self):
        self.config = Config()
        self.parser = ParserFactory.create("ast")
        self.dispatcher = Dispatcher(
            manual_types=MANUAL_TYPES,
            custom_types_requiring_llm=TYPES_REQUIRING_LLM,
        )
        self.validator = RustValidator()
        self.generator = None

    def run(self):
        env_output = os.getenv("OUTPUT_DIR")
        if env_output:
            self.config.output_dir = Path(env_output)
        elif PROTOTYPE_MODE:
            self.config.output_dir = self.config.prototype_output_dir
            print(f"🧪 Prototype mode enabled. Output dir: {self.config.output_dir}")

        api_path = self.config.incus_repo_path / self.config.api_subdir

        print(f"🔍 Parsing Go structures from {api_path}...")
        structs, enums, aliases = self.parser.parse_directory(api_path)

        parsed_struct_count = len(structs)
        parsed_enum_count = len(enums)
        parsed_alias_count = len(aliases)

        if PROTOTYPE_MODE:
            structs = self._filter_structs_for_prototype(structs)
            enums, aliases = self._filter_support_types_for_prototype(
                enums=enums,
                aliases=aliases,
                structs=structs,
            )

            print(
                f"🧪 Prototype whitelist enabled: "
                f"{len(structs)}/{parsed_struct_count} structs kept"
            )
            print(f"🧪 Prototype enums kept: {sorted(enums.keys()) or '—'}")
            print(f"🧪 Prototype aliases kept: {sorted(aliases.keys()) or '—'}")

        print("🔀 Dispatching entities...")
        dispatch_res = self.dispatcher.dispatch(structs, enums, aliases)

        self.generator = RustGenerator(dispatch_res.known_types)

        generated_files: dict[str, str] = {}
        mod_entities: list[tuple[str, str]] = []

        # --- Шаблонная генерация enum ---
        for name, enum_obj in dispatch_res.template_enums.items():
            mod_name = camel_to_snake(name)
            generated_files[f"{mod_name}.rs"] = self.generator.generate_enum(enum_obj)
            mod_entities.append((name, mod_name))

        # --- Шаблонная генерация alias ---
        for name, alias_obj in dispatch_res.template_aliases.items():
            mod_name = camel_to_snake(name)
            generated_files[f"{mod_name}.rs"] = self.generator.generate_alias(alias_obj)
            mod_entities.append((name, mod_name))

        # --- Шаблонная генерация простых struct ---
        for name, struct_obj in dispatch_res.template_structs.items():
            mod_name = camel_to_snake(name)
            generated_files[f"{mod_name}.rs"] = self.generator.generate_struct(struct_obj)
            mod_entities.append((name, mod_name))

        # --- Обработка сложных структур ---
        llm_success = 0
        llm_failed = 0
        llm_fallback = 0

        if dispatch_res.llm_structs:
            print(
                f"\n🧠 Начинаем обработку сложных структур "
                f"({len(dispatch_res.llm_structs)})..."
            )
            llm_generator = LLMGenerator()

            for name, struct_obj in dispatch_res.llm_structs.items():
                mod_name = camel_to_snake(name)

                # В текущем этапе LLM запускается только на стабильном whitelist.
                # Остальные сложные структуры временно генерируем шаблоном,
                # чтобы не ломать общий пакет.
                if name not in LLM_TEST_WHITELIST:
                    print(f"⏭️  {name}: fallback -> template")
                    generated_files[f"{mod_name}.rs"] = self.generator.generate_struct(struct_obj)
                    mod_entities.append((name, mod_name))
                    llm_fallback += 1
                    continue

                print(f"\n🧠 LLM обрабатывает структуру: {name}")
                raw_go_code = self._build_raw_go_struct(struct_obj)

                success, rust_code, info = llm_generator.generate(
                    go_struct=struct_obj,
                    validator=self.validator,
                    test_env_files={},  # пока изолированная валидация
                    raw_go_code=raw_go_code,
                )

                if success and rust_code:
                    generated_files[f"{mod_name}.rs"] = rust_code
                    mod_entities.append((name, mod_name))
                    llm_success += 1
                    print(f"✅ {name}: {info}")
                else:
                    print(f"❌ {name}: ошибка LLM -> fallback в template ({info})")
                    generated_files[f"{mod_name}.rs"] = self.generator.generate_struct(struct_obj)
                    mod_entities.append((name, mod_name))
                    llm_failed += 1

        # mod.rs должен быть сгенерирован ДО финальной валидации
        mod_content = self.generator.generate_mod_file(mod_entities)
        generated_files["mod.rs"] = mod_content

        print("\n──────── Generation Report ────────")
        print(
            f"Total entities parsed:         "
            f"{parsed_struct_count + parsed_enum_count + parsed_alias_count}"
        )
        print(f"Structs parsed:                {parsed_struct_count}")
        print(f"Enums parsed:                  {parsed_enum_count}")
        print(f"Aliases parsed:                {parsed_alias_count}")
        if PROTOTYPE_MODE:
            print(f"Structs kept in prototype:     {len(structs)}")
            print(f"Enums kept in prototype:       {len(enums)}")
            print(f"Aliases kept in prototype:     {len(aliases)}")
        print(f"Structs generated (template):  {len(dispatch_res.template_structs)}")
        print(f"Structs marked as llm:         {len(dispatch_res.llm_structs)}")
        print(f"LLM success:                   {llm_success}")
        print(f"LLM failed -> template:        {llm_failed}")
        print(f"LLM skipped -> template:       {llm_fallback}")
        print(f"Enums generated:               {len(dispatch_res.template_enums)}")
        print(f"Aliases generated:             {len(dispatch_res.template_aliases)}")
        print(f"Manual types skipped:          {len(MANUAL_TYPES)}")
        print(f"Output dir: {self.config.output_dir}")
        print("───────────────────────────────────\n")

        print("🛠️  Validating all generated files...")
        val_result = self.validator.validate_all(generated_files)

        if val_result.passed:
            print(f"✅ Validation passed! Saving {len(generated_files)} files...")

            self.config.output_dir.mkdir(parents=True, exist_ok=True)

            for old_file in self.config.output_dir.glob("*.rs"):
                old_file.unlink()

            for name, content in generated_files.items():
                (self.config.output_dir / name).write_text(content, encoding="utf-8")

            print("📦 Generated mod.rs")
            print("🚀 All done successfully!")
            return True
        else:
            print("❌ Validation failed! Files were NOT saved.")
            print(f"💡 Причина: {val_result.error_message}")
            return False

    def _filter_structs_for_prototype(self, structs: dict[str, object]) -> dict[str, object]:
        """
        Оставляет только структуры, входящие в текущий scope прототипа.
        Если whitelist будет пустым, фильтрация отключается.
        """
        if not PROTOTYPE_STRUCT_WHITELIST:
            return structs

        return {
            name: obj
            for name, obj in structs.items()
            if name in PROTOTYPE_STRUCT_WHITELIST
        }

    def _filter_support_types_for_prototype(
        self,
        enums: dict[str, object],
        aliases: dict[str, object],
        structs: dict[str, object],
    ) -> tuple[dict[str, object], dict[str, object]]:
        """
        Для прототипа оставляем только те enums/aliases, которые:
        1) явно разрешены whitelist'ом,
        2) напрямую используются выбранными struct'ами,
        3) либо нужны как зависимости уже выбранных alias'ов.
        """
        direct_refs = self._collect_referenced_type_names_from_structs(structs)

        kept_enums = set(PROTOTYPE_ENUM_WHITELIST) | (set(enums.keys()) & direct_refs)
        kept_aliases = set(PROTOTYPE_ALIAS_WHITELIST) | (set(aliases.keys()) & direct_refs)

        # Рекурсивно подтягиваем зависимости alias -> alias / enum
        changed = True
        while changed:
            changed = False

            for alias_name in list(kept_aliases):
                alias_obj = aliases.get(alias_name)
                if not alias_obj:
                    continue

                nested_tokens = self._extract_type_tokens(alias_obj.target_type)
                for token in nested_tokens:
                    if token in aliases and token not in kept_aliases:
                        kept_aliases.add(token)
                        changed = True
                    if token in enums and token not in kept_enums:
                        kept_enums.add(token)
                        changed = True

        filtered_enums = {
            name: obj
            for name, obj in enums.items()
            if name in kept_enums
        }

        filtered_aliases = {
            name: obj
            for name, obj in aliases.items()
            if name in kept_aliases
        }

        return filtered_enums, filtered_aliases

    def _collect_referenced_type_names_from_structs(self, structs: dict[str, object]) -> set[str]:
        refs = set()

        for struct_obj in structs.values():
            for field in struct_obj.fields:
                refs.update(self._extract_type_tokens(field.go_type))

        return refs

    def _extract_type_tokens(self, go_type: str) -> set[str]:
        """
        Грубое извлечение имён кастомных типов из Go-строки типа.
        Подходит для текущего этапа прототипа.
        Примеры:
        - InstanceType
        - []AccessEntry
        - map[string]MetadataConfigGroup
        """
        return set(re.findall(r"\b[A-Z][A-Za-z0-9_]*\b", go_type))

    def _build_raw_go_struct(self, struct_obj) -> str:
        lines = [f"type {struct_obj.name} struct {{"]

        for field in struct_obj.fields:
            tag_parts = []

            if field.tag.json_name is not None:
                json_tag = field.tag.json_name
                if field.tag.omitempty:
                    json_tag += ",omitempty"
                tag_parts.append(f'json:"{json_tag}"')

            if field.tag.inline:
                tag_parts.append('yaml:",inline"')

            if tag_parts:
                tag_str = " `" + " ".join(tag_parts) + "`"
            else:
                tag_str = ""

            lines.append(f"    {field.name} {field.go_type}{tag_str}")

        lines.append("}")
        return "\n".join(lines)