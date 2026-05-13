from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class GoTag:
    json_name: Optional[str] = None
    omitempty: bool = False
    inline: bool = False


@dataclass
class GoField:
    name: str
    go_type: str
    tag: GoTag
    comment: str = ""
    is_embedded: bool = False


@dataclass
class GoStruct:
    name: str
    fields: List[GoField] = field(default_factory=list)
    embedded: List[str] = field(default_factory=list)
    comment: str = ""


@dataclass
class GoEnum:
    name: str
    base_type: str
    values: List[tuple[str, str]] = field(default_factory=list)


@dataclass
class GoAlias:
    name: str
    target_type: str
