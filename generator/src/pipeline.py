import os
import re
from pathlib import Path

from src.config import Config
from src.dispatcher import Dispatcher
from src.generator.llm_generator import LLMGenerator
from src.generator.rust_generator import RustGenerator
from src.parser.factory import ParserFactory
from src.validation.validator import RustValidator


# Типы, которые пишутся вручную и не должны перезаписываться генератором
MANUAL_TYPES = {"ConfigMap", "DevicesMap"}

# Если структура содержит такие типы, она попадает в категорию "сложных"
TYPES_REQUIRING_LLM = {"ConfigMap", "DevicesMap"}

# На этапе отладки LLM даём ей только 2 структуры.
# Остальные сложные структуры временно генерируем шаблоном,
# чтобы итоговый пакет оставался полным и проходил финальную валидацию.
LLM_TEST_WHITELIST = {"ProfilePut", "InstancePut"}


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

        api_path = self.config.incus_repo_path / self.config.api_subdir

        print(f"🔍 Parsing Go structures from {api_path}...")
        structs, enums, aliases = self.parser.parse_directory(api_path)

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
            print(f"\n🧠 Начинаем обработку сложных структур ({len(dispatch_res.llm_structs)})...")
            llm_generator = LLMGenerator()

            for name, struct_obj in dispatch_res.llm_structs.items():
                mod_name = camel_to_snake(name)

                # Если структура не в whitelist для теста LLM,
                # временно генерируем её шаблоном, чтобы не ломать итоговую сборку.
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
                    test_env_files={},  # ВАЖНО: проверяем LLM-файл изолированно
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
        print(f"Total entities parsed: {len(structs) + len(enums) + len(aliases)}")
        print(f"Structs generated (template): {len(dispatch_res.template_structs)}")
        print(f"Structs marked as llm:        {len(dispatch_res.llm_structs)}")
        print(f"LLM success:                  {llm_success}")
        print(f"LLM failed -> template:       {llm_failed}")
        print(f"LLM skipped -> template:      {llm_fallback}")
        print(f"Enums generated:              {len(dispatch_res.template_enums)}")
        print(f"Aliases generated:            {len(dispatch_res.template_aliases)}")
        print(f"Manual types skipped:         {len(MANUAL_TYPES)}")
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