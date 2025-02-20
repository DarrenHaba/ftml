from typing import Dict

from ftml.document import FTMLDocument
from ftml.validator import FTMLValidator


class FTMLSchema:
    def __init__(self, schema_def: Dict):
        self.schema_def = self._normalize_schema(schema_def)

    @classmethod
    def load(cls, schema_str: str) -> "FTMLSchema":
        document = FTMLDocument.load(schema_str)
        return cls(document.to_dict())

    def validate(self, data: Dict) -> bool:
        validator = FTMLValidator(self.schema_def)
        return validator.validate(data)

    def _normalize_schema(self, schema: Dict) -> Dict:
        normalized = {}
        for key, value in schema.items():
            if isinstance(value, dict):
                # Handle nested schemas
                if 'type' in value:
                    # This is a type definition
                    normalized[key] = value
                else:
                    # This is a nested schema
                    normalized[key] = {
                        'type': 'dict',
                        'fields': self._normalize_schema(value)
                    }
            else:
                normalized[key] = {'type': value}
        return normalized
