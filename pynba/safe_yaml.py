"""Module for safe, high-performance yaml manipulation"""

from collections.abc import Mapping, Iterable

import yaml
import numpy as np


def _np_types():
    type_dict = {bool: [], np.integer: [], np.floating: [], np.character: []}
    for value in np.ScalarType:
        for py_type in type_dict:
            if (
                issubclass(value, py_type) or np.issubdtype(value, py_type)
            ) and not issubclass(value, bytes):
                type_dict[py_type].append(value)
                break
    return type_dict


NP_TYPES = _np_types()
DICT_TYPES = (Mapping,)
LIST_TYPES = (Iterable,)
SCALAR_TYPES = {
    bool: tuple(set(NP_TYPES[bool])),
    int: tuple(set(NP_TYPES[np.integer])),
    float: tuple(set(NP_TYPES[np.floating])),
    str: tuple(set(NP_TYPES[np.character])),
}


def load(stream_or_string):
    """Load yaml from stream or string"""
    return yaml.load(stream_or_string, Loader=yaml.CSafeLoader)


def dump(data, *args, **kwargs):
    """Dump data as yaml, optionally to a stream"""
    kwargs["Dumper"] = yaml.CSafeDumper
    return yaml.dump(_convert_to_native_types(data), *args, **kwargs)


def _convert_to_native_types(data):
    if data is None:
        return data
    for native_type, subclasses in SCALAR_TYPES.items():
        if isinstance(data, subclasses):
            return native_type(data)
    if isinstance(data, DICT_TYPES):
        return {
            _convert_to_native_types(key): _convert_to_native_types(val)
            for key, val in data.items()
        }
    if isinstance(data, LIST_TYPES):
        return [_convert_to_native_types(val) for val in data]
    raise TypeError(f"Data of incompatible type {type(data)} found.")
