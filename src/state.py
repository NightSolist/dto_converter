"""
Модуль работы с состоянием синхронизации.

Содержит только базовые функции чтения и записи .sync_state.
Намеренно не зависит ни от GitHub, ни от других внешних сервисов,
чтобы могло использоваться в любых CI/CD-шагах с минимальным окружением.
"""

from pathlib import Path
from typing import Optional


DEFAULT_STATE_FILE = Path("state/.sync_state")


def load_state(state_file: Path = DEFAULT_STATE_FILE) -> Optional[str]:
    """
    Загружает SHA последнего обработанного коммита из файла состояния.

    Возвращает None, если файл состояния отсутствует или пуст.
    """
    if not state_file.exists():
        return None

    value = state_file.read_text(encoding="utf-8").strip()
    return value or None


def save_state(sha: str, state_file: Path = DEFAULT_STATE_FILE) -> None:
    """
    Сохраняет SHA последнего успешно обработанного коммита.

    Создаёт каталог при необходимости.
    """
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(sha, encoding="utf-8")
    print(f"💾 .sync_state обновлён: {sha}")