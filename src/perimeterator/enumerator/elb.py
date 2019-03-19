''' Perimeterator - Enumerator for AWS ELBs (Public IPs). '''

import logging
import boto3

from perimeterator.helper import aws_elb_arn
from perimeterator.helper import dns_lookup


class Enumerator(object):
    ''' Perimeterator - Enumerator for AWS ELBs (Public IPs). '''
    # Required for Boto and reporting.
    SERVICE = 'elb'

    def __init__(self, region):
        self.logger = logging.getLogger(__name__)
        self.region = region
        self.client = boto3.client(self.SERVICE, region_name=region)

    def get(self):
        ''' Attempt to get all Public IPs from ELBs. '''
        resources = []

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

            # Lookup the DNS name for this ELB to get the current IPs. We
            # also need to construct the ARN, as it's not provided in the
            # output from a describe operation (?!)
            resources.append({
                "service": self.SERVICE,
                "identifier": aws_elb_arn(
                    self.region,
                    elb["LoadBalancerName"]
                ),
                "addresses": dns_lookup(elb["DNSName"]),
            })

        self.logger.info("Got IPs for %s resources", len(resources))
        return resources
