''' Perimeterator - Enumerator for AWS EC2 Instances (Public IPs). '''

import logging
import boto3

from perimeterator.helper import aws_ec2_arn


class Enumerator(object):
    ''' Perimeterator - Enumerator for AWS EC2 Instances (Public IPs). '''
    # Required for Boto and reporting.
    SERVICE = 'ec2'

    def __init__(self, region):
        self.logger = logging.getLogger(__name__)
        self.region = region
        self.client = boto3.client(self.SERVICE, region_name=region)

    def get(self):
        ''' Attempt to get all Public IPs from EC2 instances. '''
        resources = []
        filters = [
            {
                "Name": "instance-state-name",
                "Values": [
                    "pending",
                    "running",
                ],
            }
        ]

        # Ensure that all IPs attached to running or pending instances are
        # accounted for.
        next_token = ''
        while next_token is not None:
            if next_token:
                candidates = self.client.describe_instances(
                    Filters=filters,
                    NextToken=next_token
                )
            else:
                candidates = self.client.describe_instances(
                    Filters=filters
                )

            # Check if we need to continue paging.
            if "NextToken" in candidates:
                self.logger.debug(
                    "'NextToken' found, additional page of results to fetch"
                )
                next_token = candidates["NextToken"]
            else:
                next_token = None

            # A reservation can contain one or more instances
            for reservation in candidates["Reservations"]:
                self.logger.info(
                    "Inspecting reservation %s",
                    reservation["ReservationId"]
                )
                for instance in reservation["Instances"]:
                    self.logger.info(
                        "Inspecting instance %s", instance["InstanceId"]
                    )
                    # An instance can have multiple NICs.
                    addresses = []
                    for nic in instance["NetworkInterfaces"]:
                        # A NIC can have multiple IPs.
                        for ip in nic["PrivateIpAddresses"]:
                            # An IP may not have an association if it is only
                            # an RFC1918 address.
                            if "Association" in ip and "PublicIp" in ip["Association"]:
                                addresses.append(
                                    ip["Association"]["PublicIp"]
                                )

                    # We need to construct the EC2 instance ARN ourselves, as
                    # this isn't provided as part of the describe output.
                    resources.append({
                        "service": self.SERVICE,
                        "identifier": aws_ec2_arn(
                            self.region,
                            instance["InstanceId"]
                        ),
                        "addresses": addresses,
                    })

        self.logger.info("Got IPs for %s resources", len(resources))
        return resources
