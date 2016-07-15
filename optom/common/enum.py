class Enum(tuple):
    __getattr__ = tuple.index
