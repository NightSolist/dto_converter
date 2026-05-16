import json
import os
from pathlib import Path

from src.config import Config
from src.dispatcher import Dispatcher
from src.email_notifier import EmailNotifier, EmailNotifierError
from src.generator.llm_generator import LLMGenerator
from src.generator.rust_generator import RustGenerator, camel_to_snake
from src.parser.factory import ParserFactory
from src.validation.validator import RustValidator


PROTOTYPE_MODE = True

PROTOTYPE_STRUCT_WHITELIST = {
    "Network",
    "NetworkPut",
    "NetworksPost",
    "Profile",
    "ProfilePut",
    "ProfilesPost",
    "StoragePool",
    "StoragePoolPut",
    "StoragePoolsPost",
    "InstancePut",
    "InstancesPost",
    "InstanceSource",
    "InstanceStatePut",
    "Operation",
}

PROTOTYPE_ENUM_WHITELIST = {
    "InstanceType",
    "StatusCode",
}

PROTOTYPE_ALIAS_WHITELIST = {
    "ConfigMap",
    "DevicesMap",
}


class Pipeline:
    def __init__(self):
        self.config = Config()
        self.parser = ParserFactory.create("ast")
        self.dispatcher = Dispatcher()
        self.validator = RustValidator()
        self.llm_generator = LLMGenerator()
        self.generator = None

    def run(self) -> bool:
        env_output = os.getenv("OUTPUT_DIR")
        if env_output:
            self.config.output_dir = Path(env_output)
        elif PROTOTYPE_MODE:
            self.config.output_dir = self.config.prototype_output_dir
            print(
                f"🧪 Prototype mode enabled. "
                f"Output dir: {self.config.output_dir}"
            )

        api_path = self.config.incus_repo_path / self.config.api_subdir

        print(f"🔍 Parsing Go structures from {api_path}...")
        structs, enums, aliases = self.parser.parse_directory(api_path)

        parsed_struct_count = len(structs)
        parsed_enum_count = len(enums)
        parsed_alias_count = len(aliases)

        if PROTOTYPE_MODE:
            structs = {
                k: v for k, v in structs.items()
                if k in PROTOTYPE_STRUCT_WHITELIST
            }
            enums = {
                k: v for k, v in enums.items()
                if k in PROTOTYPE_ENUM_WHITELIST
            }
            aliases = {
                k: v for k, v in aliases.items()
                if k in PROTOTYPE_ALIAS_WHITELIST
            }
            print(
                f"🧪 Prototype filter: "
                f"{len(structs)} structs, "
                f"{len(enums)} enums, "
                f"{len(aliases)} aliases"
            )

        dispatch_res = self.dispatcher.dispatch(structs, enums, aliases)
        self.generator = RustGenerator(dispatch_res.known_types)

        generated_files: dict[str, str] = {}
        mod_entities: list[tuple[str, str]] = []
        failed_entities: list[dict] = []

        # Уже успешно сгенерированные файлы.
        # Они передаются в validate_single как support_files
        test_env_files: dict[str, str] = {}

        # ============================================================
        # 1. ALIASES
        # ============================================================
        print(f"\n── Aliases ({len(dispatch_res.aliases)}) ──")
        for name, alias_obj in sorted(dispatch_res.aliases.items()):
            mod_name = camel_to_snake(name)
            filename = f"{mod_name}.rs"
            print(f"\n📙 {name}")

            template_code = self.generator.generate_alias(alias_obj)
            template_res = self.validator.validate_single(
                filename, template_code, test_env_files
            )

            if template_res.passed:
                generated_files[filename] = template_code
                test_env_files[filename] = template_code
                mod_entities.append((name, mod_name))
                print("   ✅ template passed")
                continue

            print(
                f"   ⚠️ template error: "
                f"{template_res.error_message}"
            )

            raw_go = self._build_raw_go_alias(alias_obj)
            success, repaired, info = self.llm_generator.repair(
                entity_name=name,
                raw_go_code=raw_go,
                template_rust_code=template_code,
                initial_error=template_res.error_message or "Unknown error",
                validator=self.validator,
                test_env_files=test_env_files,
                filename=filename,
            )

            if success and repaired:
                generated_files[filename] = repaired
                test_env_files[filename] = repaired
                mod_entities.append((name, mod_name))
                print(f"   ✅ llm repair passed ({info})")
            else:
                failed_entities.append({
                    "name": name,
                    "kind": "alias",
                    "error": info,
                })
                print(f"   ❌ failed: {info}")

        # ============================================================
        # 2. ENUMS
        # ============================================================
        print(f"\n── Enums ({len(dispatch_res.enums)}) ──")
        for name, enum_obj in sorted(dispatch_res.enums.items()):
            mod_name = camel_to_snake(name)
            filename = f"{mod_name}.rs"
            print(f"\n📘 {name}")

            template_code = self.generator.generate_enum(enum_obj)
            template_res = self.validator.validate_single(
                filename, template_code, test_env_files
            )

            if template_res.passed:
                generated_files[filename] = template_code
                test_env_files[filename] = template_code
                mod_entities.append((name, mod_name))
                print("   ✅ template passed")
                continue

            print(
                f"   ⚠️ template error: "
                f"{template_res.error_message}"
            )

            raw_go = self._build_raw_go_enum(enum_obj)
            success, repaired, info = self.llm_generator.repair(
                entity_name=name,
                raw_go_code=raw_go,
                template_rust_code=template_code,
                initial_error=template_res.error_message or "Unknown error",
                validator=self.validator,
                test_env_files=test_env_files,
                filename=filename,
            )

            if success and repaired:
                generated_files[filename] = repaired
                test_env_files[filename] = repaired
                mod_entities.append((name, mod_name))
                print(f"   ✅ llm repair passed ({info})")
            else:
                failed_entities.append({
                    "name": name,
                    "kind": "enum",
                    "error": info,
                })
                print(f"   ❌ failed: {info}")

        # ============================================================
        # 3. STRUCTS — МНОГОПРОХОДНАЯ ШАБЛОННАЯ ГЕНЕРАЦИЯ
        # ============================================================
        print(f"\n── Structs ({len(dispatch_res.structs)}) ──")

        pending_structs = dict(sorted(dispatch_res.structs.items()))
        postponed_structs: dict[str, object] = {}

        wave = 1
        while pending_structs:
            print(f"\n🔁 Struct generation wave #{wave}")
            progress_made = False
            postponed_structs.clear()

            for name, struct_obj in pending_structs.items():
                mod_name = camel_to_snake(name)
                filename = f"{mod_name}.rs"
                print(f"\n📗 {name}")

                template_code = self.generator.generate_struct(struct_obj)
                template_res = self.validator.validate_single(
                    filename, template_code, test_env_files
                )

                if template_res.passed:
                    generated_files[filename] = template_code
                    test_env_files[filename] = template_code
                    mod_entities.append((name, mod_name))
                    progress_made = True
                    print("   ✅ template passed")
                else:
                    error_text = template_res.error_message or ""
                    print(f"   ⚠️ template error: {error_text}")

                    if self._is_missing_dependency_error(error_text):
                        print(
                            "   ⏳ dependency not ready yet, "
                            "postponing to next wave"
                        )
                        postponed_structs[name] = struct_obj
                    else:
                        postponed_structs[name] = struct_obj

            if progress_made:
                pending_structs = dict(postponed_structs)
                wave += 1
                continue

            # Если в этой волне не было прогресса —
            # дальше шаблон уже не поможет, переходим к LLM repair
            break

        # ============================================================
        # 4. LLM REPAIR для оставшихся struct
        # ============================================================
        if postponed_structs:
            print(
                f"\n🤖 Running LLM repair for remaining "
                f"{len(postponed_structs)} struct(s)..."
            )

        for name, struct_obj in postponed_structs.items():
            mod_name = camel_to_snake(name)
            filename = f"{mod_name}.rs"
            print(f"\n📗 {name}")

            template_code = self.generator.generate_struct(struct_obj)
            template_res = self.validator.validate_single(
                filename, template_code, test_env_files
            )

            raw_go = self._build_raw_go_struct(struct_obj)
            success, repaired, info = self.llm_generator.repair(
                entity_name=name,
                raw_go_code=raw_go,
                template_rust_code=template_code,
                initial_error=template_res.error_message or "Unknown error",
                validator=self.validator,
                test_env_files=test_env_files,
                filename=filename,
            )

            if success and repaired:
                generated_files[filename] = repaired
                test_env_files[filename] = repaired
                mod_entities.append((name, mod_name))
                print(f"   ✅ llm repair passed ({info})")
            else:
                failed_entities.append({
                    "name": name,
                    "kind": "struct",
                    "error": info,
                })
                print(f"   ❌ failed: {info}")

        # ============================================================
        # 5. Если есть провалы — уведомление и остановка
        # ============================================================
        if failed_entities:
            print(
                "\n❌ Есть сущности, которые не удалось "
                "синхронизировать:"
            )
            for item in failed_entities:
                print(
                    f"   ✗ {item['name']} "
                    f"({item['kind']}): {item['error']}"
                )
            self._notify_engineer(failed_entities)
            return False

        # ============================================================
        # 6. mod.rs
        # ============================================================
        mod_content = self.generator.generate_mod_file(mod_entities)
        generated_files["mod.rs"] = mod_content

        # ============================================================
        # 7. Финальная валидация
        # ============================================================
        print("\n──────── Generation Report ────────")
        print(
            f"Entities parsed:  "
            f"{parsed_struct_count + parsed_enum_count + parsed_alias_count}"
        )
        print(f"Structs:          {parsed_struct_count}")
        print(f"Enums:            {parsed_enum_count}")
        print(f"Aliases:          {parsed_alias_count}")
        if PROTOTYPE_MODE:
            print(
                f"After prototype filter: "
                f"{len(structs)} structs, "
                f"{len(enums)} enums, "
                f"{len(aliases)} aliases"
            )
        print(f"Generated:        {len(mod_entities)}")
        print(f"Failed:           {len(failed_entities)}")
        print(f"Output dir:       {self.config.output_dir}")
        print("───────────────────────────────────\n")

        print("🛠️  Final validation...")
        val_result = self.validator.validate_all(generated_files)

        if val_result.passed:
            print(
                f"✅ Validation passed! "
                f"Saving {len(generated_files)} files..."
            )
            self.config.output_dir.mkdir(
                parents=True, exist_ok=True
            )

            for old_file in self.config.output_dir.glob("*.rs"):
                old_file.unlink()

            for name, content in generated_files.items():
                (self.config.output_dir / name).write_text(
                    content, encoding="utf-8"
                )

            print("🚀 All done successfully!")
            return True
        else:
            print("❌ Final validation failed!")
            print(f"   Причина: {val_result.error_message}")
            self._notify_engineer([{
                "name": "final_validation",
                "kind": "pipeline",
                "error": val_result.error_message or "Unknown",
            }])
            return False

    def _is_missing_dependency_error(self, error_text: str) -> bool:
        """
        Возвращает True, если ошибка шаблонной генерации
        вызвана тем, что зависимый тип ещё не был сгенерирован
        и не попал в support_files.
        """
        lowered = error_text.lower()
        return (
            "unresolved import `crate::incus::" in lowered
            or "not found in `crate::incus`" in lowered
            or "no `crate::incus::" in lowered
        )

    def _notify_engineer(self, failed_entities: list[dict]) -> None:
        changes_file = Path("state/changes.json")
        changed_files = []
        commit_sha = None

        if changes_file.exists():
            try:
                changes = json.loads(
                    changes_file.read_text(encoding="utf-8")
                )
                commit_sha = changes.get("last_sha")
                changed_files = [
                    f["path"]
                    for f in changes
                    .get("api_changes", {})
                    .get("files", [])
                ]
            except Exception as e:
                print(
                    f"⚠️ Не удалось прочитать "
                    f"state/changes.json: {e}"
                )

        print(
            "\n⚠️ Уведомляем инженера о невозможности "
            "синхронизации..."
        )
        try:
            notifier = EmailNotifier()
            notifier.send_sync_failure_notification(
                failed_entities=failed_entities,
                changed_files=changed_files,
                commit_sha=commit_sha,
            )
        except EmailNotifierError as e:
            print(f"⚠️ Email не отправлен: {e}")
            print("   Детали провала:")
            for item in failed_entities:
                print(
                    f"   ✗ {item['name']} "
                    f"({item['kind']}): {item['error']}"
                )

    def _build_raw_go_struct(self, struct_obj) -> str:
        lines = [f"type {struct_obj.name} struct {{"]

        for emb in getattr(struct_obj, "embedded", []):
            lines.append(f'    {emb} `yaml:",inline"`')

        for field in struct_obj.fields:
            tag_parts = []
            if field.tag.json_name is not None:
                json_tag = field.tag.json_name
                if field.tag.omitempty:
                    json_tag += ",omitempty"
                tag_parts.append(f'json:"{json_tag}"')
            if field.tag.inline:
                tag_parts.append('yaml:",inline"')
            tag_str = (
                " `" + " ".join(tag_parts) + "`"
                if tag_parts
                else ""
            )
            lines.append(
                f"    {field.name} {field.go_type}{tag_str}"
            )

        lines.append("}")
        return "\n".join(lines)

    def _build_raw_go_enum(self, enum_obj) -> str:
        lines = [
            f"type {enum_obj.name} {enum_obj.base_type}",
            "",
            "const (",
        ]
        for name, value in enum_obj.values:
            lines.append(
                f"    {name} {enum_obj.name} = {value}"
            )
        lines.append(")")
        return "\n".join(lines)

    def _build_raw_go_alias(self, alias_obj) -> str:
        return f"type {alias_obj.name} {alias_obj.target_type}"