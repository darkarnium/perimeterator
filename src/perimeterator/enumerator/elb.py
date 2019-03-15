''' Perimeterator - Enumerator for AWS ELBs (Public IPs). '''

import logging
import boto3

from perimeterator.enumerator.helper import dns_lookup


class Enumerator(object):
    ''' Perimeterator - Enumerator for AWS ELBs (Public IPs). '''

    def __init__(self, region):
        self.logger = logging.getLogger(__name__)
        self.client = boto3.client('elb', region_name=region)

    def get(self):
        ''' Attempt to get all Public IPs from ELBs. '''
        addresses = []

        # Ensure that all IPs attached to all internet facing ELBs.
        #
        # TODO: NextMarker
        candidates = self.client.describe_load_balancers()

        # For some odd reason the AWS API doesn't appear to allow a filter
        # on describe operations for ELBs, so we'll have to filter manually.
        for elb in candidates["LoadBalancerDescriptions"]:
            self.logger.debug(
                "Inspecting ELB %s", elb["LoadBalancerName"],
            )
            if elb["Scheme"] != "internet-facing":
                self.logger.debug("ELB is not internet facing")
                continue

            # Lookup the DNS name for this ELB to get the current IPs.
            addresses.extend(dns_lookup(elb["DNSName"]))

        self.logger.info("Got %s IPs", len(addresses))
        return addresses
