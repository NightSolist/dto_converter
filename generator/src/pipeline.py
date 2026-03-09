import os
from pathlib import Path

from src.config import Config
from src.generator.rust_generator import RustGenerator
from src.generator.type_mapping import is_supported_type
from src.parser.factory import ParserFactory
from src.validation.validator import RustValidator


class Pipeline:
    def __init__(self):
        self.config = Config()
        self.parser = ParserFactory.create("ast")
        self.validator = RustValidator()

    def run(self):
        # Поддержка ENV для output_dir (чтобы переопределять без правки config.py)
        env_output = os.getenv("OUTPUT_DIR")
        if env_output:
            self.config.output_dir = Path(env_output)

        api_path = self.config.incus_repo_path / self.config.api_subdir

        structs, enums, aliases = self.parser.parse_directory(api_path)

        known_types = set(structs.keys()) | set(enums.keys()) | set(aliases.keys())

        self.generator = RustGenerator(known_types)

        total = len(structs) + len(enums) + len(aliases)
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        generated_files = {}

        # 1. Enums
        for name, enum in enums.items():
            rust_code = self.generator.generate_enum(enum)
            generated_files[f"{name.lower()}.rs"] = rust_code

        # 2. Aliases
        for name, alias in aliases.items():
            rust_code = self.generator.generate_alias(alias)
            generated_files[f"{name.lower()}.rs"] = rust_code

        # 3. Structs
        for name, struct in structs.items():
            rust_code = self.generator.generate_struct(struct)
            generated_files[f"{name.lower()}.rs"] = rust_code

        print("\n──────── Generation Report ────────")
        print(f"Total entities found: {total}")
        print(f"Generated files: {len(generated_files)}")
        print(f"Output dir: {self.config.output_dir}")
        print("───────────────────────────────────\n")

        print("Validating all generated files...")
        valid = self.validator.validate_all(generated_files)

        # Сохраняем файлы (даже если валидация не прошла, для отладки)
        print(f"💾 Saving files...")
        for name, content in generated_files.items():
            (self.config.output_dir / name).write_text(content)

        # Генерация mod.rs
        mod_content = "// Auto-generated. Do not edit.\n\n"
        for name in sorted(generated_files.keys()):
            mod_name = name.replace(".rs", "")
            mod_content += f"pub mod {mod_name};\n"

        (self.config.output_dir / "mod.rs").write_text(mod_content)
        print("📦 Generated mod.rs")

        if valid:
            print("✅ All generated files compile successfully!")
        else:
            print("❌ Some files failed compilation. Check logs above.")
