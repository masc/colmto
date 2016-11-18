# -*- coding: utf-8 -*-
"""Helper module"""


class Enum(tuple):
    """Enum class for python 2"""
    __getattr__ = tuple.index


class Namespace(object):
    """Namespace similar to argparse"""
    # pylint: disable=too-few-public-methods
    def __init__(self, **kwargs):
        """C'tor."""
        self.__dict__.update(kwargs)
