from typing import Any
import os
from .constants import IGNORED


def to_dependencies(id_prefix: str, target: dict) -> list[tuple]:
    output: list[tuple] = []
    for window_id, components in target.items():
        for component in components:
            component_type, attr = component.split('.')
            output.append((f'{id_prefix}-{window_id}-{component_type}', attr))
    return output


def merge_children(items: list[Any]) -> list:
    result = []
    for i in items:
        if not isinstance(i, list):
            result.append(i)
        else:
            for k in i:
                result.append(k)
    return result


def get_clear_args(args):
    return {arg: value for arg, value in args.items() if arg != 'self'}


def get_names(path):
    return [item.replace('.py', '') for item in os.listdir(path) if item not in IGNORED]

