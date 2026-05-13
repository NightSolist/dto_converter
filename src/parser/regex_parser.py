import re
from pathlib import Path
from typing import Dict, Tuple

from src.parser.base import GoParserInterface
from src.parser.go_types import GoAlias, GoEnum, GoField, GoStruct, GoTag


class RegexParser(GoParserInterface):
    def parse_directory(
        self, api_dir: Path
    ) -> Tuple[Dict[str, GoStruct], Dict[str, GoEnum], Dict[str, GoAlias]]:
        structs: Dict[str, GoStruct] = {}

        for go_file in api_dir.glob("*.go"):
            if go_file.name.endswith("_test.go"):
                continue
            parsed = self.parse_file(go_file)
            for s in parsed:
                structs[s.name] = s

        # Regex парсер не поддерживает Enum и Alias
        return structs, {}, {}

    def parse_file(self, file_path: Path):
        content = file_path.read_text(encoding="utf-8")
        structs = []

        pattern = re.compile(r"type\s+(\w+)\s+struct\s*\{", re.MULTILINE)

        for match in pattern.finditer(content):
            name = match.group(1)
            body = self._extract_block(content, match.end())
            fields = self._parse_fields(body)
            structs.append(GoStruct(name=name, fields=fields))

        return structs

    def _extract_block(self, content: str, start: int) -> str:
        depth = 1
        i = start
        while i < len(content) and depth > 0:
            if content[i] == "{":
                depth += 1
            elif content[i] == "}":
                depth -= 1
            i += 1
        return content[start : i - 1]

    def _parse_fields(self, body: str):
        fields = []
        for line in body.split("\n"):
            line = line.strip()
            if not line or line.startswith("//"):
                continue

            tag = GoTag()

            tag_match = re.search(r"`([^`]*)`", line)
            if tag_match:
                raw = tag_match.group(1)
                json_match = re.search(r'json:"([^"]*)"', raw)
                if json_match:
                    parts = json_match.group(1).split(",")
                    tag.json_name = parts[0]
                    tag.omitempty = "omitempty" in parts

                yaml_match = re.search(r'yaml:"([^"]*)"', raw)
                if yaml_match:
                    parts = yaml_match.group(1).split(",")
                    tag.inline = "inline" in parts

                line = line[: tag_match.start()].strip()

            parts = line.split()
            if len(parts) >= 2:
                fields.append(
                    GoField(
                        name=parts[0],
                        go_type=parts[1],
                        tag=tag,
                    )
                )

        return fields
