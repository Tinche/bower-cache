"""A small compatibility layer for Python 3."""

try:
    reload = reload
except NameError:
    import imp
    reload = imp.reload