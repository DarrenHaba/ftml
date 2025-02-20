from typing import Dict, List, Union


class FTMLSerializer:
    @staticmethod
    def serialize(data: Union[Dict, List], indent=0, is_top_level=True) -> str:
        if isinstance(data, dict):
            return FTMLSerializer.serialize_dict(data, indent, is_top_level)
        elif isinstance(data, list):
            return FTMLSerializer.serialize_list(data, indent, is_top_level)
        else:
            return FTMLSerializer.serialize_value(data)

    @staticmethod
    def serialize_dict(data: Dict, indent=0, is_top_level=False) -> str:
        if is_top_level:
            return FTMLSerializer.serialize_top_level_dict(data, indent)

        lines = []
        spaces = ' ' * indent
        lines.append(f'{spaces}{{')

        for key, value in data.items():
            key_str = f'"{key}"' if ' ' in key else key
            value_str = FTMLSerializer.serialize(value, indent + 4, False)
            lines.append(f'{spaces}    {key_str} = {value_str},')

        lines.append(f'{spaces}}}')
        return '\n'.join(lines)

    @staticmethod
    def serialize_list(data: List, indent=0, is_top_level=False) -> str:
        if is_top_level:
            return FTMLSerializer.serialize_top_level_list(data, indent)

        if not data:
            return '[]'

        if all(FTMLSerializer._is_simple(v) for v in data):
            return '[' + ', '.join(FTMLSerializer.serialize_value(v) for v in data) + ']'

        spaces = ' ' * indent
        lines = [f'{spaces}[']
        for item in data:
            item_str = FTMLSerializer.serialize(item, indent + 4, False)
            lines.append(f'{spaces}    {item_str},')
        lines.append(f'{spaces}]')
        return '\n'.join(lines)

    @staticmethod
    def _is_simple(value) -> bool:
        return isinstance(value, (str, int, float, bool)) or value is None

    @staticmethod
    def serialize_value(value) -> str:
        if isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, bool):
            return 'true' if value else 'false'
        elif value is None:
            return 'null'
        else:
            return str(value)

    @staticmethod
    def serialize_top_level_dict(data: Dict, indent=0) -> str:
        lines = []
        items = list(data.items())
        for i, (key, value) in enumerate(items):
            key_str = f'"{key}"' if ' ' in key else key
            value_str = FTMLSerializer.serialize(value, indent + 4, False)
            line = f'{key_str} = {value_str}'
            if i < len(items) - 1:
                line += ','
            lines.append(line)
        return '\n'.join(lines)

    @staticmethod
    def serialize_top_level_list(data: List, indent=0) -> str:
        items = []
        for i, item in enumerate(data):
            item_str = FTMLSerializer.serialize_value(item)
            if i < len(data) - 1:
                item_str += ','
            items.append(item_str)
        return '\n'.join(items)
