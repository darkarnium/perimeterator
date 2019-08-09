''' Perimeterator - Enumerator for AWS RDS instances (Public). '''

import logging
import boto3

from perimeterator.helper import dns_lookup


class Enumerator(object):
    ''' Perimeterator - Enumerator for AWS RDS instances (Public). '''
    # Required for Boto and reporting.
    SERVICE = 'rds'

    def __init__(self, region):
        self.logger = logging.getLogger(__name__)
        self.region = region
        self.client = boto3.client(self.SERVICE, region_name=region)

    def get(self):
        ''' Attempt to get all Public IPs from RDS instances. '''
        resources = []

        # Once again, the AWS API doesn't appear to allow filtering by RDS
        # instances where PubliclyAccessible is True. As a result, we'll
        # need to do this manually
        marker = ''
        while marker is not None:
            if marker:
                candidates = self.client.describe_db_instances(Marker=marker)
            else:
                candidates = self.client.describe_db_instances()

            # Check if we need to continue paging.
            if "Marker" in candidates:
                self.logger.debug(
                    "'Marker' found, additional page of results to fetch"
                )
                marker = candidates["Marker"]
            else:
                marker = None

            for rds in candidates["DBInstances"]:
                # Skip instances still being created as they may not yet have
                # endpoints created / generated.
                if rds["DBInstanceStatus"] == "creating":
                    self.logger.debug(
                        "Skipping instance as it's still being provisioned"
                    )
                    continue

                self.logger.debug(
                    "Inspecting RDS instance %s",
                    rds["DBInstanceIdentifier"]
                )
                if not rds["PubliclyAccessible"]:
                    self.logger.debug("RDS instance is not internet facing")
                    continue

                # Lookup the DNS name to get the current IPs. We're ignoring
                # the configured port for the time being, although this could
                # present a trivial optimisation for scanning speed up.
                try:
                    resources.append({
                        "service": self.SERVICE,
                        "identifier": rds["DBInstanceArn"],
                        "addresses": dns_lookup(rds["Endpoint"]["Address"]),
                    })
                except KeyError:
                    self.logger.warning(
                        "Skipping RDS instance %s due to error when enumerating endpoints",
                        rds["DBInstanceArn"]
                    )

        self.logger.info("Got IPs for %s resources", len(resources))
        return resources
