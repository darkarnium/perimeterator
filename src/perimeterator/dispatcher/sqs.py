''' Perimeterator - SQS dispatcher for enumerated addresses. '''

import logging
import boto3
import json


class Dispatcher(object):
    ''' Perimeterator - SQS dispatcher for enumerated addresses. '''

    def __init__(self, region, queue):
        self.queue = queue
        self.logger = logging.getLogger(__name__)
        self.client = boto3.client("sqs", region_name=region)

    def dispatch(self, region, account, addresses):
        ''' Iterates over address array and enqueues for processing. '''
        self.logger.info(
            "Attempting to enqueue %d addresses", len(addresses),
        )
        for address in addresses:
            response = self.client.send_message(
                QueueUrl=self.queue,
                MessageAttributes={
                    "Region": {
                        "DataType": "String",
                        "StringValue": region,
                    },
                    "Account": {
                        "DataType": "Number",
                        "StringValue": account,
                    }
                },
                MessageBody=address
            )
            self.logger.info(
                "%s enqueued as %s", address, response["MessageId"],
            )
