from src.parser.ast_parser import ASTParser
from src.parser.regex_parser import RegexParser


class ParserFactory:
    @staticmethod
    def create(backend: str = "regex"):
        if backend == "regex":
            return RegexParser()
        elif backend == "ast":
            return ASTParser()
        else:
            raise ValueError(f"Unknown parser backend: {backend}")
