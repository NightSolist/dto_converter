import shutil
import subprocess
import tempfile
from pathlib import Path


class RustValidator:

    def validate_all(self, files: dict[str, str]) -> bool:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            src_dir = tmp_path / "src"
            src_dir.mkdir()

            (tmp_path / "Cargo.toml").write_text(
                """
[package]
name = "test"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = { version = "1", features = ["derive"] }
chrono = { version = "0.4", features = ["serde"] }
serde_json = "1"
"""
            )

            mod_lines = []

            for name, content in files.items():
                file_path = src_dir / name
                file_path.write_text(content)
                mod_name = name.replace(".rs", "")
                mod_lines.append(f"pub mod {mod_name};")

            (src_dir / "lib.rs").write_text("\n".join(mod_lines))

            print("Running cargo check...")
            result = subprocess.run(
                ["cargo", "check"],
                cwd=tmp_path,
            )

            print(f"Cargo return code: {result.returncode}")

            return result.returncode == 0
