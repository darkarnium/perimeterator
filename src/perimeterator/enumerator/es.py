''' Perimeterator - Enumerator for AWS Elasticsearch instances. '''

import logging
import boto3

from perimeterator.helper import dns_lookup


class Enumerator(object):
    ''' Perimeterator - Enumerator for AWS Elasticsearch instances. '''
    # Required for Boto and reporting.
    SERVICE = 'es'

    def __init__(self, region):
        self.logger = logging.getLogger(__name__)
        self.region = region
        self.client = boto3.client(self.SERVICE, region_name=region)

    def get(self):
        ''' Attempt to get IPs associated with Elasticsearch endpoints. '''
        resources = []

        # Get a list of all domains and then manually prune it based on
        # whether the domains are created, being deleted, etc.
        candidates = self.client.list_domain_names()

        for es in candidates["DomainNames"]:
            # Query for data about this domain based on the enumerated name.
            domain = self.client.describe_elasticsearch_domain(
                DomainName=es["DomainName"]
            )
            
            self.logger.debug("Inspecting ES domain %s", es["DomainName"])
            if domain["DomainStatus"]["Created"] == False:
                self.logger.debug(
                    "Skipping ES domain as it's still being provisioned"
                )
                continue

            if domain["DomainStatus"]["Deleted"] == True:
                self.logger.debug(
                    "Skipping ES domain as it's currently being deleted"
                )
                continue

            # Skip VPC endpoints.
            if "Endpoints" in domain["DomainStatus"]:
                self.logger.debug(
                    "Skipping ES domain as it has VPC only endpoints"
                )
                continue

            # Lookup the DNS name to get the current IPs.
            try:
                resources.append({
                    "service": self.SERVICE,
                    "identifier": domain["DomainStatus"]["ARN"],
                    "addresses": dns_lookup(
                        domain["DomainStatus"]["Endpoint"]
                    ),
                })
            except KeyError:
                self.logger.warning(
                    "Skipping ES domain due to error when enumerating endpoints",
                )

        self.logger.info("Got IPs for %s resources", len(resources))
        return resources
