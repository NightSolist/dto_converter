import json
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ValidationResult:
    passed: bool
    error_message: Optional[str] = None


class RustValidator:
    def __init__(self, cargo_timeout_seconds: int = 120):
        self.cargo_timeout_seconds = cargo_timeout_seconds

    def check_syntax(self, rust_code: str) -> ValidationResult:
        if "```" in rust_code:
            return ValidationResult(
                False,
                "Синтаксическая ошибка: "
                "найдены markdown-артефакты (```).",
            )

        if rust_code.count("{") != rust_code.count("}"):
            return ValidationResult(
                False,
                "Синтаксическая ошибка: "
                "дисбаланс фигурных скобок {}",
            )

        if rust_code.count("(") != rust_code.count(")"):
            return ValidationResult(
                False,
                "Синтаксическая ошибка: "
                "дисбаланс круглых скобок ()",
            )

        if rust_code.count("[") != rust_code.count("]"):
            return ValidationResult(
                False,
                "Синтаксическая ошибка: "
                "дисбаланс квадратных скобок []",
            )

        if not re.search(
            r"\bpub\s+(struct|enum|type|fn)\s+\w+",
            rust_code,
        ):
            return ValidationResult(
                False,
                "Синтаксическая ошибка: "
                "не найдено объявление pub struct/enum/type/fn",
            )

        return ValidationResult(True)

    def validate_all(
        self, files: dict[str, str]
    ) -> ValidationResult:
        for name, content in files.items():
            if name == "mod.rs":
                continue
            syn_res = self.check_syntax(content)
            if not syn_res.passed:
                return ValidationResult(
                    False,
                    f"В файле {name}: {syn_res.error_message}",
                )

        return self._validate_in_temp_project(files)

    def validate_single(
        self,
        filename: str,
        content: str,
        support_files: Optional[dict[str, str]] = None,
    ) -> ValidationResult:
        files = dict(support_files or {})
        files[filename] = content
        return self.validate_all(files)

    def _validate_in_temp_project(
        self, files: dict[str, str]
    ) -> ValidationResult:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            src_dir = tmp_path / "src"
            src_dir.mkdir()

            incus_dir = src_dir / "incus"
            incus_dir.mkdir()

            cargo_toml = (
                "[package]\n"
                'name = "test"\n'
                'version = "0.1.0"\n'
                'edition = "2021"\n'
                "\n"
                "[dependencies]\n"
                "serde = "
                '{ version = "1", features = ["derive"] }\n'
                "chrono = "
                '{ version = "0.4", features = ["serde"] }\n'
                'serde_json = "1"\n'
            )
            (tmp_path / "Cargo.toml").write_text(
                cargo_toml, encoding="utf-8"
            )

            for name, content in files.items():
                (incus_dir / name).write_text(
                    content, encoding="utf-8"
                )

            mod_path = incus_dir / "mod.rs"

            if mod_path.exists():
                mod_content = mod_path.read_text(
                    encoding="utf-8"
                )
            else:
                mod_lines = []
                use_lines = []

                for name in files.keys():
                    if name == "mod.rs":
                        continue
                    mod_name = Path(name).stem
                    mod_lines.append(
                        f"pub mod {mod_name};"
                    )

                    content = files[name]
                    pub_types = self._extract_pub_types(
                        content
                    )
                    for pub_type in pub_types:
                        use_lines.append(
                            f"pub use {mod_name}::{pub_type};"
                        )

                    pub_fns = self._extract_pub_fns(content)
                    for pub_fn in pub_fns:
                        use_lines.append(
                            f"pub use {mod_name}::{pub_fn};"
                        )

                mod_content = (
                    "\n".join(sorted(mod_lines))
                    + "\n\n"
                    + "\n".join(sorted(use_lines))
                    + "\n"
                )

            mod_path.write_text(
                mod_content, encoding="utf-8"
            )
            (src_dir / "lib.rs").write_text(
                "pub mod incus;\n", encoding="utf-8"
            )

            try:
                result = subprocess.run(
                    [
                        "cargo",
                        "check",
                        "--message-format=json",
                    ],
                    cwd=tmp_path,
                    capture_output=True,
                    text=True,
                    timeout=self.cargo_timeout_seconds,
                )
            except subprocess.TimeoutExpired:
                return ValidationResult(
                    False,
                    f"Таймаут cargo check "
                    f"({self.cargo_timeout_seconds}с)",
                )

            if result.returncode == 0:
                return ValidationResult(True)

            error_msg = self._extract_cargo_error(
                result.stdout, result.stderr
            )
            return ValidationResult(False, error_msg)

    def _extract_pub_types(
        self, rust_code: str
    ) -> list[str]:
        """
        Извлекает имена pub struct, pub enum, pub type
        из Rust-кода для автоматического реэкспорта
        во временном mod.rs.
        """
        types = []
        patterns = [
            r"pub\s+struct\s+(\w+)",
            r"pub\s+enum\s+(\w+)",
            r"pub\s+type\s+(\w+)",
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, rust_code):
                types.append(match.group(1))
        return types

    def _extract_pub_fns(
        self, rust_code: str
    ) -> list[str]:
        """
        Извлекает имена pub fn из Rust-кода
        для реэкспорта helper-функций
        (deserialize_config_map и т.д.)
        """
        fns = []
        for match in re.finditer(
            r"pub\s+fn\s+(\w+)", rust_code
        ):
            fns.append(match.group(1))
        return fns

    def _extract_cargo_error(
        self, stdout: str, stderr: str
    ) -> str:
        errors = []

        for line in stdout.splitlines():
            line = line.strip()
            if not line.startswith("{"):
                continue

            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue

            if msg.get("reason") != "compiler-message":
                continue

            diagnostic = msg.get("message", {})
            if diagnostic.get("level") != "error":
                continue

            text = diagnostic.get(
                "message", "Неизвестная ошибка"
            )
            spans = diagnostic.get("spans", [])

            if spans:
                primary = next(
                    (
                        s
                        for s in spans
                        if s.get("is_primary")
                    ),
                    spans[0],
                )
                file_name = primary.get("file_name", "")
                line_start = primary.get("line_start", "")
                col_start = primary.get(
                    "column_start", ""
                )
                prefix = (
                    f"[{file_name}:{line_start}:{col_start}] "
                )
            else:
                prefix = ""

            rendered = diagnostic.get("rendered")
            if rendered:
                rendered = (
                    self._strip_ansi(rendered).strip()
                )
                errors.append(prefix + rendered)
            else:
                errors.append(prefix + text)

        if errors:
            return "\n\n".join(errors[:3])

        fallback = self._strip_ansi(stderr).strip()
        if fallback:
            return "\n".join(
                fallback.splitlines()[-20:]
            )

        stdout_fallback = self._strip_ansi(stdout).strip()
        if stdout_fallback:
            return "\n".join(
                stdout_fallback.splitlines()[-20:]
            )

        return "Неизвестная ошибка компиляции"

    def _strip_ansi(self, text: str) -> str:
        ansi_escape = re.compile(
            r"\x1B\[[0-?]*[ -/]*[@-~]"
        )
        return ansi_escape.sub("", text)