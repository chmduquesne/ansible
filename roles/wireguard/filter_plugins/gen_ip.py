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
        return gen_uint32(h, forbidden)
    else:
        return res


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


def add_pubkey(config, host):
    c = dict(config)
    if 'pubkey' in c:
        return c
    if host not in c['peers']:
        raise AnsibleFilterError('pubkey missing for "%s"' % host)
    c['pubkey'] = c['peers'][host]['pubkey']
    return c


def remove_peer(config, host):
    c = dict(config)
    peers = dict(c['peers'])
    if host in peers:
        del peers[host]
    c['peers'] = peers
    return c


def auto_assign_ips(config):
    c = dict(config)

    subnets = c.get('auto_assign_ips', [])
    if not subnets:
        return c

    address = c.get('address', [])
    if not isinstance(address, list):
        raise AnsibleFilterError('Expecting "address" to be a list')

    for subnet in subnets:
        address += [ gen_ip(c['pubkey'], subnet=subnet, with_prefixlen=True) ]
    c['address'] = address

    for host, peervars in c.get('peers', dict()).items():
        allowedips = peervars.get('allowedips', [])
        if not isinstance(allowedips, list):
            raise AnsibleFilterError('Expecting "allowedips" to be a list')

        for subnet in subnets:
            allowedips += [ gen_ip(peervars['pubkey'], subnet=subnet, with_maxprefixlen=True) ]
        c['peers'][host]['allowedips'] = allowedips

    return c


class FilterModule(object):
    """
    create a pseudo-random ip address from a string
    """

    def filters(self):
        return {
            'gen_ip': gen_ip,
            'auto_assign_ips': auto_assign_ips,
            'remove_peer': remove_peer,
            'add_pubkey': add_pubkey,
        }
