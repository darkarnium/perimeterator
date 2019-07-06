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

        # Iterate over results until AWS no longer returns a 'NextMarker' in
        # order to ensure all results are retrieved.
        marker = ''
        while marker is not None:
            # Unfortunately, Marker=None or Marker='' is invalid for this API
            # call, so it looks like we can't just set this to a None value,
            # or use a ternary here.
            if marker:
                candidates = self.client.describe_load_balancers(
                    Marker=marker
                )
            else:
                candidates = self.client.describe_load_balancers()

            # Check if we need to continue paging.
            if "NextMarker" in candidates:
                self.logger.debug(
                    "'NextMarker' found, additional page of results to fetch"
                )
                marker = candidates["NextMarker"]
            else:
                marker = None

            # For some odd reason the AWS API doesn't appear to allow a
            # filter on describe operations for ELBs, so we'll have to filter
            # manually.
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
