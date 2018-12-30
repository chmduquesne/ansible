from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from jinja2 import Environment, FileSystemLoader
from ansible import errors
from ansible.module_utils._text import to_text
from ansible.errors import AnsibleFilterError
import ipaddress
import hashlib
import sys
import json


def sha256(s):
    return hashlib.sha256(s.encode()).digest()


def gen_ip(s, subnet='2001:db8::/48', with_prefixlen=False,
        with_maxprefixlen=False):
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
    ip_bytes = bytearray()

    if sys.version_info.major < 3:
        for m, t, h in zip(mask, tail, head):
            ip_bytes.append(ord(h)&ord(m)|ord(t)&(ord(m)^255))
    else:
        for m, t, h in zip(mask, tail, head):
            ip_bytes.append(h&m|t&(m^255))

    cls = network.netmask.__class__
    res = to_text(cls(bytes(ip_bytes)))

    if with_prefixlen and with_maxprefixlen:
        raise AnsibleFilterError("|gen_ip: you need to choose between prefixlen and maxprefixlen")

    if with_prefixlen:
        res += "/%d" % network.prefixlen

    if with_maxprefixlen:
        res += "/%d" % network.netmask.max_prefixlen

    return to_text(res)


def auto_assign_ips(config, host):
    c = dict(config)

    subnets = c.get('auto_assign_ips', [])
    if not subnets:
        return c

    if host not in c['peers']:
        raise AnsibleFilterError('%s not found in "peers"' % host)
    pubkey = c['peers'][host]['pubkey']

    address = c.get('address', [])
    if not isinstance(address, list):
        raise AnsibleFilterError('Expecting "address" to be a list')

    for subnet in subnets:
        address += [ gen_ip(pubkey, subnet=subnet, with_prefixlen=True) ]
    c['address'] = address

    for host, peervars in c.get('peers', dict()).items():
        allowedips = peervars.get('allowedips', [])
        if not isinstance(allowedips, list):
            raise AnsibleFilterError('Expecting "allowedips" to be a list')

        for subnet in subnets:
            allowedips += [ gen_ip(peervars['pubkey'], subnet=subnet, with_maxprefixlen=True) ]
        c['peers'][host]['allowedips'] = allowedips

    return dict(c)


class FilterModule(object):
    """
    create a pseudo-random ip address from a string
    """

    def filters(self):
        return {
            'gen_ip': gen_ip,
            'auto_assign_ips': auto_assign_ips
        }


#d = {
#        "auto_assign_ips": [
#            "10.0.0.0/8",
#            "fd1a:6126:2887::/48",
#            "2001:bc8:3a53:2::/64"
#        ],
#        "listenport": 500,
#        "mtu": 1360,
#        "out_gw": {
#            "interface": "enp0s20"
#        },
#        "peers": {
#            "dedibox": {
#                "pubkey": "aTtMVKe4OEsdK+hTcqiaRAKI6eZtyuTdy2jTAHL+e08="
#            },
#            "moviebox": {
#                "pubkey": "uI/MzgCdWyh3YcrKIA4SBd4U441DEsckIOJqxjxyaE0="
#            },
#            "op3t": {
#                "pubkey": "tuyKLuVJ8LwAut7lb4dGKsEVfFkIoIASnGgjymtsSH8="
#            },
#            "raspberrypi": {
#                "allowedips": ["2001:bc8:3a53:1::/64"],
#                "pubkey": "xKsITz2UCFdco1s2OdL+i9+8DBglDzLLS6S64MeVCi4="
#            },
#            "t450": {
#                "pubkey": "nmwGdVs+24O9KMo5zlqyAQCLz3qEaHO9HliXARd5xFg="
#            }
#        },
#        "privkey": "AIiwnm1deR5flW+iU/8ksQOZiB0HjqNQhVAbSdSlEHs=",
#        "pubkey": "aTtMVKe4OEsdK+hTcqiaRAKI6eZtyuTdy2jTAHL+e08=",
#        "public_addr": "163.172.50.192"
#    }
#
#print(auto_assign_ips(d))
