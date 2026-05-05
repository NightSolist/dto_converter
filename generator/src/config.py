from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    incus_repo_path: Path = Path.home() / "data/repos/incus"
    api_subdir: str = "shared/api"

    # Основной каталог полного generated-пакета
    output_dir: Path = Path.home() / "dto_converter/client/src/incus/generated"

    # Отдельный каталог для прототипного subset-пакета
    prototype_output_dir: Path = Path.home() / "dto_converter/client/src/incus/generated_prototype"