from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from jinja2 import Environment, FileSystemLoader
from ansible import errors

# printf "%d" "0x$(echo -n "$1" | sha256sum | cut -b-4)"
def as_uint32(s, forbidden=[]):
    import hashlib
    h = hashlib.sha256(s.encode()).hexdigest()
    res = int(h[:4], 16)
    if res in forbidden:
        return uint32(h, forbidden)
    else:
        return res

class FilterModule(object):
    '''
    create a pseudo-random uint32 from a string

    '''
    def filters(self):
        return { 'as_uint32': as_uint32 }
