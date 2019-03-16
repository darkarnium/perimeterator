''' Perimeterator - Enumerator for AWS RDS instances (Public). '''

import logging
import boto3

from perimeterator.enumerator.helper import dns_lookup


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
        # need to do this manually.
        #
        # TODO: NextMarker
        candidates = self.client.describe_db_instances()

        for rds in candidates["DBInstances"]:
            self.logger.debug(
                "Inspecting RDS instance %s", rds["DBInstanceIdentifier"],
            )
            if rds["PubliclyAccessible"] != True:
                self.logger.debug("RDS instance is not internet facing")
                continue

            # Lookup the DNS name for this ELB to get the current IPs. We're
            # ignoring the configured port for the time being, although this
            # could present a trivial optimisation for scanning speed up.
            resources.append({
                "service": self.SERVICE,
                "identifier": rds["DBInstanceArn"],
                "addresses": dns_lookup(rds["Endpoint"]["Address"]),
            })

        self.logger.info("Got IPs for %s resources", len(resources))
        return resources
