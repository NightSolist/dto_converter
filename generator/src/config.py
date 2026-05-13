import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    # Локальный клон Go-репозитория-источника
    incus_repo_path: Path = Path(
        os.getenv("INCUS_REPO_PATH", str(Path.home() / "data/repos/incus-fork-demo"))
    )

    api_subdir: str = "shared/api"

    # Основной каталог полного generated-пакета
    output_dir: Path = Path.home() / "incus-lab-manager" / "src" / "incus" / "generated"

    # Отдельный каталог для prototype subset
    prototype_output_dir: Path = Path.home() / "incus-lab-manager" / "src" / "incus" / "generated_prototype"