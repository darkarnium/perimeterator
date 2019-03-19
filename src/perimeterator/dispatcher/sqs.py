''' Perimeterator - SQS dispatcher for enumerated addresses. '''

import logging
import boto3
import json

from perimeterator.helper import aws_sqs_queue_url


class Dispatcher(object):
    ''' Perimeterator - SQS dispatcher for enumerated addresses. '''

    def __init__(self, queue):
        self.queue = aws_sqs_queue_url(queue)
        self.logger = logging.getLogger(__name__)
        self.client = boto3.client("sqs")

    def dispatch(self, account, resources):
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
