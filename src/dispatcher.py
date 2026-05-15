from dataclasses import dataclass
from typing import Dict

from src.parser.go_types import GoAlias, GoEnum, GoStruct


@dataclass
class DispatchResult:
    structs: Dict[str, GoStruct]
    enums: Dict[str, GoEnum]
    aliases: Dict[str, GoAlias]
    known_types: set[str]


class Dispatcher:
    """
    Все типы обрабатываются по единому правилу:
    шаблонная генерация -> валидация ->
    LLM repair -> уведомление инженера.

    Никаких исключений по типу структуры.
    ConfigMap и DevicesMap участвуют наравне со всеми.
    """

    def dispatch(
        self,
        structs: Dict[str, GoStruct],
        enums: Dict[str, GoEnum],
        aliases: Dict[str, GoAlias],
    ) -> DispatchResult:

        known_types = (
            set(structs.keys())
            | set(enums.keys())
            | set(aliases.keys())
        )

        return DispatchResult(
            structs=structs,
            enums=enums,
            aliases=aliases,
            known_types=known_types,
        )