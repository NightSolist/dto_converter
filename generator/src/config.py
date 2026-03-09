from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    incus_repo_path: Path = Path.home() / "data/repos/incus"
    api_subdir: str = "shared/api"
    output_dir: Path = Path.home() / "data/output"
