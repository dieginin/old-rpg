import sys


def str_to_class(classname: str):
    return getattr(sys.modules[__name__], classname)
