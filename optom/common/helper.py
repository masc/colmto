# -*- coding: utf-8 -*-
"""Helper module"""


class Enum(tuple):
    """Enum class for python 2"""
    __getattr__ = tuple.index


class Namespace:
    """Namespace similar to argparse"""
    def __init__(self, **kwargs):
        """C'tor."""
        self.__dict__.update(kwargs)