''' Perimeterator - Enumerator for AWS ELBv2 (Public IPs). '''

import boto3
import logging

from perimeterator.enumerator.helper import dns_lookup


class Enumerator(object):
    ''' Perimeterator - Enumerator for AWS ELBv2 (Public IPs). '''

    def __init__(self, region):
        self.logger = logging.getLogger(__name__)
        self.client = boto3.client('elbv2', region_name=region)

    def get(self):
        ''' Attempt to get all Public IPs from ELBv2 instances. '''
        addresses = []

        # Ensure that all IPs attached to all internet facing ELBv2
        # instances.
        candidates = self.client.describe_load_balancers()

        # For some odd reason the AWS API doesn't appear to allow a filter
        # on describe operations for ELBs, so we'll have to filter manually.
        #
        # TODO: NextMarker
        for elb in candidates["LoadBalancers"]:
            self.logger.debug(
                "Inspecting ELBv2 instance %s", elb["LoadBalancerArn"],
            )
            if elb["Scheme"] != "internet-facing":
                self.logger.debug("ELBv2 instance is not internet facing")
                continue

            # If a network load balancer, IPs will be present in the describe
            # output. If not, then we'll need to resolve the DNS name to get
            # the current LB IPs.
            if "LoadBalancerAddresses" in elb["AvailabilityZones"][0]:
                for az in elb["AvailabilityZones"]:
                    # Each AZ has an associated IP allocation.
                    for address in az["LoadBalancerAddresses"]:
                        addresses.append(address["IpAddress"])
            else:
                addresses.extend(dns_lookup(elb["DNSName"]))

        self.logger.info("Got %s IPs", len(addresses))
        return addresses
