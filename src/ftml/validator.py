from typing import Dict, Any, List

from ftml.exceptions import ValidationError


class FTMLValidator:
    def __init__(self, schema: Dict):
        self.schema = schema

    def validate(self, data: Dict) -> bool:
        # First check for duplicate keys in the data
        self._check_duplicate_keys(data)

        # Then validate against schema
        for key, schema_def in self.schema.items():
            self._validate_field(key, schema_def, data)
        return True

    @staticmethod
    def _check_duplicate_keys(data: Dict):
        seen_keys = set()
        for key in data.keys():
            if key in seen_keys:
                raise ValidationError(f"Duplicate key '{key}' found in data")
            seen_keys.add(key)

    def _validate_value(self, key: str, value: Any, schema_def: Dict):
        # Handle nested structures
        if isinstance(value, dict) and 'type' in schema_def and schema_def['type'].startswith('dict'):
            self._validate_dict(value, schema_def)
        elif isinstance(value, list) and 'type' in schema_def and schema_def['type'].startswith('list'):
            self._validate_list(value, schema_def)
        else:
            self._check_type(value, schema_def.get('type'))

    def _validate_dict(self, value: Dict, schema_def: Dict):
        if not isinstance(value, dict):
            raise ValidationError(f"Expected dict, got {type(value).__name__}")
        for field, field_schema in schema_def.get('fields', {}).items():
            if field in value:
                self._validate_value(field, value[field], field_schema)
            else:
                if 'default' in field_schema:
                    value[field] = field_schema['default']  # Inject nested default
                elif not field_schema.get('optional', False):
                    raise ValidationError(f"Missing required field: {field}")

    @staticmethod
    def _handle_multiplicity(data: Dict):
        for key in list(data.keys()):
            if any(key.endswith(sym) for sym in ('?', '*', '+')):
                clean_key = key.rstrip('?*+')
                values = data.pop(key)
                if not isinstance(values, list):
                    values = [values]
                data[clean_key] = values

    def _validate_field(self, key: str, schema_def: dict, data: dict):
        clean_key = key.rstrip('?*+')
        multiplicity = key[-1] if key[-1] in ('?', '*', '+') else None

        if multiplicity:
            items = data.get(clean_key, [])
            if multiplicity == '+' and len(items) < 1:
                raise ValidationError(f"Field {clean_key}+ requires at least one item")
            if multiplicity == '?' and len(items) > 1:
                raise ValidationError(f"Field {clean_key}? allows maximum one item")
            for item in items:
                self._check_type(item, schema_def['type'])
        else:
            if clean_key in data:
                value = data[clean_key]
            else:
                if 'default' in schema_def:
                    value = schema_def['default']
                    data[clean_key] = value  # Inject default into data
                elif schema_def.get('optional'):
                    return
                else:
                    raise ValidationError(f"Missing required field: {clean_key}")
            if 'fields' in schema_def:
                if not isinstance(value, dict):
                    raise ValidationError(f"Expected dict for field {clean_key}, got {type(value).__name__}")
                self._validate_dict(value, schema_def)
            else:
                self._check_type(value, schema_def['type'])

    def _validate_list(self, value: List, schema_def: Dict):
        if not isinstance(value, list):
            raise ValidationError(f"Expected list, got {type(value).__name__}")

        # Validate each item in the list
        item_type = schema_def.get('item_type')
        if item_type:
            for item in value:
                self._check_type(item, item_type)

    def _check_type(self, value: Any, expected_type: str):
        if expected_type is None:
            return

        type_map = {
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'dict': dict,
            'list': list,
            'null': type(None)
        }

        # Handle union types
        if '|' in expected_type:
            types = [t.strip() for t in expected_type.split('|')]
            if not any(self._is_valid_type(value, t, type_map) for t in types):
                raise ValidationError(
                    f"Type mismatch. Expected one of {types}, got {type(value).__name__}"
                )
        else:
            if not self._is_valid_type(value, expected_type, type_map):
                raise ValidationError(
                    f"Type mismatch. Expected {expected_type}, got {type(value).__name__}"
                )

    @staticmethod
    def _is_valid_type(value: Any, type_name: str, type_map: Dict) -> bool:
        if type_name == 'null' and value is None:
            return True
        return isinstance(value, type_map.get(type_name, object))

    def _type_map(self, type_name: str) -> type:
        return {
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'null': type(None)
        }.get(type_name, object)

