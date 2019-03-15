''' Perimeterator - Enumerator for AWS EC2 Instances (Public IPs). '''

import logging
import boto3


class Enumerator(object):
    ''' Perimeterator - Enumerator for AWS EC2 Instances (Public IPs). '''

    def __init__(self, region):
        self.logger = logging.getLogger(__name__)
        self.client = boto3.client('ec2', region_name=region)

    def get(self):
        ''' Attempt to get all Public IPs from EC2 instances. '''
        addresses = []

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
                for nic in instance["NetworkInterfaces"]:
                    # A NIC can have multiple IPs.
                    for ip in nic["PrivateIpAddresses"]:
                        # An IP may not have an association if it is only
                        # an RFC1918 address.
                        if "Association" in ip and "PublicIp" in ip["Association"]:
                            self.logger.info(
                                "Instance %s has IP %s bound, recording",
                                instance["InstanceId"],
                                ip["Association"]["PublicIp"],
                            )
                            addresses.append(ip["Association"]["PublicIp"])

        self.logger.info("Got %s IPs", len(addresses))
        return addresses
