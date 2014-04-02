"""Python 2/3 compatibility module."""
import sys

PY2 = sys.version_info[0] == 2

if PY2:
    import urlparse
else:
    from urllib import parse as urlparse
