from typing import Dict

from ftml.exceptions import ValidationError
from ftml.parser import FTMLParser
from ftml.serializer import FTMLSerializer
from ftml.tokenizer import FTMLTokenizer
from ftml.validator import FTMLValidator


class FTMLDocument:
    def __init__(self, data: Dict, schema: Dict = None):
        self.data = data
        self.schema = schema

    @classmethod
    def load(cls, data: str, schema: Dict = None) -> "FTMLDocument":
        tokenizer = FTMLTokenizer(data)
        tokens = tokenizer.tokenize()
        parser = FTMLParser(tokens)
        parsed_data = parser.parse()

        if schema:
            validator = FTMLValidator(schema)
            if not validator.validate(parsed_data):
                raise ValidationError("Schema validation failed")

        return cls(parsed_data, schema)

    @classmethod
    def from_dict(cls, data: Dict) -> "FTMLDocument":
        return cls(data)

    def to_dict(self) -> Dict:
        return self.data

    def to_ftml(self) -> str:
        return FTMLSerializer.serialize(self.data)
