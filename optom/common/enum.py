# -*- coding: utf-8 -*-
"""Enum class for python 2"""


class Enum(tuple):
    """Enum class for python 2"""
    __getattr__ = tuple.index
