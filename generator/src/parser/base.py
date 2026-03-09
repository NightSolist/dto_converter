from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Tuple

from src.parser.go_types import GoAlias, GoEnum, GoStruct


class GoParserInterface(ABC):
    @abstractmethod
    def parse_directory(
        self, api_dir: Path
    ) -> Tuple[Dict[str, GoStruct], Dict[str, GoEnum], Dict[str, GoAlias]]:
        """
        Парсит директорию и возвращает структуры, перечисления и алиасы.
        :param api_dir: Путь к директории API
        :return: (structs, enums, aliases)
        """
        pass
