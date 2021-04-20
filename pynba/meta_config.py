"""Module for creating nicely typed Config objects"""

from abc import ABCMeta


def _make_property(name, attr_type):
    return property(
        lambda self: attr_type(self._settings[name])  # pylint: disable=protected-access
    )


class MetaConfig(ABCMeta):
    """Metaclass for the Config object"""

    def __new__(cls, name, bases, namespace, **kwargs):
        annotations = namespace.get("__annotations__", {})
        for attr_name, attr_type in annotations.items():
            namespace[attr_name] = _make_property(attr_name, attr_type)

        return super().__new__(cls, name, bases, namespace, **kwargs)


class AbstractConfig(metaclass=MetaConfig):  # pylint: disable=too-few-public-methods
    """Abstract base class to inherit from for a Config object"""

    def __init__(self, settings):
        self._settings = settings
