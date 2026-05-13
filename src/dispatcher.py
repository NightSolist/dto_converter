from dataclasses import dataclass
from typing import Dict

from src.parser.go_types import GoAlias, GoEnum, GoStruct


@dataclass
class DispatchResult:
    template_structs: Dict[str, GoStruct]
    template_enums: Dict[str, GoEnum]
    template_aliases: Dict[str, GoAlias]
    llm_structs: Dict[str, GoStruct]
    manual_types: set[str]
    known_types: set[str]


class Dispatcher:
    def __init__(self, manual_types: set[str], custom_types_requiring_llm: set[str]):
        self.manual_types = manual_types
        self.custom_types_requiring_llm = custom_types_requiring_llm

    def dispatch(
        self,
        structs: Dict[str, GoStruct],
        enums: Dict[str, GoEnum],
        aliases: Dict[str, GoAlias],
    ) -> DispatchResult:
        result = DispatchResult(
            template_structs={},
            template_enums={},
            template_aliases={},
            llm_structs={},
            manual_types=self.manual_types,
            known_types=set(),
        )

        result.known_types = (
            set(structs.keys())
            | set(enums.keys())
            | set(aliases.keys())
            | self.manual_types
        )

        # Enum всегда в шаблонный генератор
        for name, enum_obj in enums.items():
            if name in self.manual_types:
                continue
            result.template_enums[name] = enum_obj

        # Alias всегда в шаблонный генератор
        for name, alias_obj in aliases.items():
            if name in self.manual_types:
                continue
            result.template_aliases[name] = alias_obj

        # Struct: либо template, либо llm
        for name, struct_obj in structs.items():
            if name in self.manual_types:
                continue

            requires_llm = False
            for field in struct_obj.fields:
                if any(t in field.go_type for t in self.custom_types_requiring_llm):
                    requires_llm = True
                    break

            if requires_llm:
                print(f"🧠 Структура {name} отправлена в LLM-генерацию")
                result.llm_structs[name] = struct_obj
            else:
                result.template_structs[name] = struct_obj

        return result