''' Perimeterator - Internal helpers for Enumerator operations. '''

import socket


def dns_lookup(fqdn):
    ''' Lookups up the given FQDN returning an array of IPs. '''
    addresses = []
    try:
        # Provide a port number as '0' as we only want to trigger a DNS
        # lookup, no more, no less.
        for info in socket.getaddrinfo(fqdn, 0):
            addresses.append(info[4][0])
    except socket.gaierror:
        # This is super janky, but hey.
        pass

    return addresses
