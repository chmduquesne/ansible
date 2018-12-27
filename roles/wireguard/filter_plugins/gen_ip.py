from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from jinja2 import Environment, FileSystemLoader
from ansible import errors
from ansible.module_utils._text import to_text
import ipaddress
import hashlib
import sys
import json


def sha256(s):
    return hashlib.sha256(s.encode()).digest()


def gen_ip(s, subnet='2001:db8::/48'):
    """
    - Hash the input
    - Take the first bytes of the result
    - Mask those bytes with the input subnet
    """
    if sys.version_info.major < 3:
        subnet = unicode(subnet)

    try:
        network = ipaddress.IPv4Network(subnet)
    except:
        network = ipaddress.IPv6Network(subnet)

    mask = network.netmask.packed
    head = network.network_address.packed
    tail = sha256(s + '\n')
    res = bytearray()

    if sys.version_info.major < 3:
        for m, t, h in zip(mask, tail, head):
            res.append(ord(h)&ord(m)|ord(t)&(ord(m)^255))
    else:
        for m, t, h in zip(mask, tail, head):
            res.append(h&m|t&(m^255))

    cls = network.netmask.__class__
    return str(cls(bytes(res)))



class FilterModule(object):
    """
    create a pseudo-random ip address from a string
    """

    def filters(self):
        return {
            'gen_ip': gen_ip,
        }
