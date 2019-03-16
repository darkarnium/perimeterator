''' Perimeterator - Internal helpers for Enumerator operations. '''

import boto3
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


def aws_account_id():
    ''' Attempts to get the account id for the current AWS account. '''
    client = boto3.client('sts')
    return client.get_caller_identity()["Account"]
