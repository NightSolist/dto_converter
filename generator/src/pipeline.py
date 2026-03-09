import os
from pathlib import Path
from src.config import Config
from src.parser.factory import ParserFactory
from src.generator.rust_generator import RustGenerator
from src.validation.validator import RustValidator

# БЕЛЫЙ СПИСОК: генерируем .rs файлы только для этих сущностей
TARGET_ENTITIES = {
    "InstancesPost",
    "InstanceSource",
    "InstanceType",
    "InstanceStatePut",
    "NetworksPost",
    "ConfigMap",
    "DevicesMap",
}

class Pipeline:
    def __init__(self):
        self.config = Config()
        self.parser = ParserFactory.create("ast")
        self.validator = RustValidator()

    def run(self):
        env_output = os.getenv("OUTPUT_DIR")
        if env_output:
            self.config.output_dir = Path(env_output)

        api_path = self.config.incus_repo_path / self.config.api_subdir
        
        # 1. Парсим ВСЕ структуры из Go
        # AST-парсер УЖЕ внутри себя делает _resolve_embeddings по полному словарю.
        # Значит, поля InstancePut уже скопировались внутрь InstancesPost.
        structs, enums, aliases = self.parser.parse_directory(api_path)

        # 2. Оставляем для генерации только то, что в белом списке
        filtered_structs = {k: v for k, v in structs.items() if k in TARGET_ENTITIES}
        filtered_enums = {k: v for k, v in enums.items() if k in TARGET_ENTITIES}
        filtered_aliases = {k: v for k, v in aliases.items() if k in TARGET_ENTITIES}

        # Известные типы собираем из отфильтрованных, чтобы импорты были только на них
        known_types = set(filtered_structs.keys()) | set(filtered_enums.keys()) | set(filtered_aliases.keys())
        
        self.generator = RustGenerator(known_types)

        total_filtered = len(filtered_structs) + len(filtered_enums) + len(filtered_aliases)
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        generated_files = {}

        for name, enum in filtered_enums.items():
            generated_files[f"{name.lower()}.rs"] = self.generator.generate_enum(enum)

        for name, alias in filtered_aliases.items():
            generated_files[f"{name.lower()}.rs"] = self.generator.generate_alias(alias)

        for name, struct in filtered_structs.items():
            generated_files[f"{name.lower()}.rs"] = self.generator.generate_struct(struct)

        print("\n──────── Generation Report ────────")
        print(f"Total entities parsed: {len(structs) + len(enums) + len(aliases)}")
        print(f"Entities in Whitelist: {total_filtered}")
        print(f"Structs generated: {len(filtered_structs)}")
        print(f"Enums generated: {len(filtered_enums)}")
        print(f"Aliases generated: {len(filtered_aliases)}")
        print(f"Output dir: {self.config.output_dir}")
        print("───────────────────────────────────\n")

        print("Validating all generated files...")
        valid = self.validator.validate_all(generated_files)

        print(f"💾 Saving {len(generated_files)} files to {self.config.output_dir}...")
        for name, content in generated_files.items():
            (self.config.output_dir / name).write_text(content)

        # Генерация mod.rs только для сгенерированных файлов
        mod_content = "// Auto-generated minimal DTOs\n\n"
        for name in sorted(generated_files.keys()):
            mod_name = name.replace(".rs", "")
            mod_content += f"pub mod {mod_name};\n"
        
        (self.config.output_dir / "mod.rs").write_text(mod_content)
        print("📦 Generated mod.rs")

        if valid:
            print("✅ All generated files compile successfully!")
        else:
            print("❌ Some files failed compilation. Check logs above.")