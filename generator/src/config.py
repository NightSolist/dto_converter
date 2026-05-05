from dataclasses import dataclass
from pathlib import Path

@dataclass
class Config:
    incus_repo_path: Path = Path.home() / "data/repos/incus"
    api_subdir: str = "shared/api"
    
    # Путь к папке generated внутри Rust-проекта
    # Замените путь, если ваш incus-lab-manager лежит в другом месте!
    output_dir: Path = Path.home() / "dto_converter/client/src/incus/generated"