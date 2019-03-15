''' Perimeterator - Enumerator for AWS EIPs (Elastic IPs). '''

import logging
import boto3


class Enumerator(object):
    ''' Perimeterator - Enumerator for AWS EIPs (Elastic IPs). '''

    def __init__(self, region):
        self.logger = logging.getLogger(__name__)
        self.client = boto3.client('ec2', region_name=region)

    def get(self):
        ''' Attempt to get all Public IP from EIPs. '''
        addresses = []
        candidates = self.client.describe_addresses()
        for candidate in candidates:
            addresses.append(candidate['PublicIp'])

        return addresses
