''' Perimeterator - SQS dispatcher for enumerated addresses. '''

import logging
import boto3
import json


class Dispatcher(object):
    ''' Perimeterator - SQS dispatcher for enumerated addresses. '''

    def __init__(self, region, queue):
        self.queue = queue
        self.logger = logging.getLogger(__name__)
        self.region = region
        self.client = boto3.client("sqs", region_name=region)

    def dispatch(self, region, account, resources):
        ''' Iterates over address array and enqueues for processing. '''
        self.logger.info(
            "Attempting to enqueue %d resources", len(resources),
        )
        for resource in resources:
            response = self.client.send_message(
                QueueUrl=self.queue,
                MessageAttributes={
                    "Identifier": {
                        "DataType": "String",
                        "StringValue": resource["identifier"],
                    },
                    "Service": {
                        "DataType": "String",
                        "StringValue": resource["service"],
                    }
                },
                MessageBody=json.dumps(resource["addresses"])
            )
            self.logger.info(
                "Enqueued IPs for resource %s as %s",
                resource["identifier"],
                response["MessageId"],
            )
