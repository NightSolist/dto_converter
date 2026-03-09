import json
import logging
import re
import subprocess
from pathlib import Path
from typing import Dict, Tuple

from src.parser.base import GoParserInterface
from src.parser.go_types import GoAlias, GoEnum, GoField, GoStruct, GoTag

logger = logging.getLogger(__name__)


class ASTParser(GoParserInterface):
    def __init__(self):
        self.tool_path = Path(__file__).parent.parent / "go-ast-parser" / "parser"

    def parse_directory(
        self, api_dir: Path
    ) -> Tuple[Dict[str, GoStruct], Dict[str, GoEnum], Dict[str, GoAlias]]:
        if not self.tool_path.exists():
            raise RuntimeError(f"Go AST tool not found at {self.tool_path}")

        cmd = [str(self.tool_path), "-dir", str(api_dir)]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"AST parser failed: {result.stderr}")

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse AST JSON: {e}")

        structs: Dict[str, GoStruct] = {}
        enums: Dict[str, GoEnum] = {}
        aliases: Dict[str, GoAlias] = {}

        for pkg in data:
            raw_structs = pkg.get("structs") or []
            for s_data in raw_structs:
                go_struct = self._convert_struct(s_data)
                structs[go_struct.name] = go_struct

            raw_enums = pkg.get("enums") or []
            for e_data in raw_enums:
                go_enum = self._convert_enum(e_data)
                enums[go_enum.name] = go_enum

            raw_aliases = pkg.get("aliases") or []
            for a_data in raw_aliases:
                aliases[a_data["name"]] = GoAlias(
                    name=a_data["name"], target_type=a_data["type"]
                )

        self._resolve_embeddings(structs)

        return structs, enums, aliases

    def _convert_struct(self, data: dict) -> GoStruct:
        fields = []
        raw_fields = data.get("fields") or []
        embedded = data.get("embedded") or []

        for f_data in raw_fields:
            tag = self._parse_tag(f_data.get("tag", ""))
            fields.append(
                GoField(
                    name=f_data["name"],
                    go_type=f_data["type"],
                    tag=tag,
                    is_embedded=False,
                )
            )

        return GoStruct(
            name=data["name"],
            fields=fields,
            embedded=embedded,
            comment=data.get("comment", ""),
        )

    def _convert_enum(self, data: dict) -> GoEnum:
        values = []
        for v in data.get("values", []):
            values.append((v["name"], v["value"]))

        return GoEnum(name=data["name"], base_type=data["type"], values=values)

    def _parse_tag(self, raw_tag: str) -> GoTag:
        tag = GoTag()
        if not raw_tag:
            return tag

        json_match = re.search(r'json:"([^"]*)"', raw_tag)
        if json_match:
            parts = json_match.group(1).split(",")
            tag.json_name = parts[0]
            tag.omitempty = "omitempty" in parts

        yaml_match = re.search(r'yaml:"([^"]*)"', raw_tag)
        if yaml_match:
            parts = yaml_match.group(1).split(",")
            tag.inline = "inline" in parts

        return tag

    def _resolve_embeddings(self, structs: Dict[str, GoStruct]):
        for name, struct in structs.items():
            if not struct.embedded:
                continue

            for embedded_name in struct.embedded:
                clean_name = embedded_name.lstrip("*").split(".")[-1]

                if clean_name in structs:
                    parent = structs[clean_name]
                    struct.fields.extend(parent.fields)
