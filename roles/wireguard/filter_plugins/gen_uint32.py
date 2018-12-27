from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from jinja2 import Environment, FileSystemLoader
from ansible import errors
import hashlib

def gen_uint32(s, forbidden=[0, 253, 254, 255]):
    """
    - Hash the input
    - Take the first 4 bytes of the result
    - Interpret as a uint32

    Can be reproduced in shell:

    printf "%d" "0x$(echo -n "$1" | sha256sum | cut -b-4)"
    """
    h = hashlib.sha256(s.encode()).hexdigest()
    res = int(h[:4], 16)
    if res in forbidden:
        return uint32(h, forbidden)
    else:
        return res

class FilterModule(object):
    """
    Create a pseudo-random uint32 from a string
    """
    def filters(self):
        return { 'gen_uint32': gen_uint32 }
