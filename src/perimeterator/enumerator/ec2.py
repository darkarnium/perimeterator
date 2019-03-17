''' Perimeterator - Enumerator for AWS EC2 Instances (Public IPs). '''

import logging
import boto3

from perimeterator.helper import ec2_arn


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

        # Ensure that all IPs attached to running or pending instances, are
        # accounted for.
        #
        # TODO: NextToken
        candidates = self.client.describe_instances(
            Filters=[
                {
                    "Name": "instance-state-name",
                    "Values": [
                        "pending",
                        "running",
                    ],
                }
            ]
        )

        # A reservation can contain one or more instances
        for reservation in candidates["Reservations"]:
            self.logger.debug(
                "Inspecting reservation %s", reservation["ReservationId"],
            )
            for instance in reservation["Instances"]:
                self.logger.debug(
                    "Inspecting instance %s", instance["InstanceId"],
                )
                # An instance can have multiple NICs.
                addresses = []
                for nic in instance["NetworkInterfaces"]:
                    # A NIC can have multiple IPs.
                    for ip in nic["PrivateIpAddresses"]:
                        # An IP may not have an association if it is only an
                        # RFC1918 address.
                        if "Association" in ip and "PublicIp" in ip["Association"]:
                            addresses.append(ip["Association"]["PublicIp"])

                # We need to construct the EC2 instance ARN ourselves, as
                # this isn't provided as part of the describe output.
                resources.append({
                    "service": self.SERVICE,
                    "identifier": ec2_arn(self.region, instance["InstanceId"]),
                    "addresses": addresses,
                })

        self.logger.info("Got IPs for %s resources", len(resources))
        return resources
