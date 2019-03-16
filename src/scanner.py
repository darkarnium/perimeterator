#!/usr/bin/env python3
''' Perimeterator Scanner.

Provides scanning of resources identified by the Perimeterator Enumerator.
'''

import os
import boto3
import logging

import perimeterator


def main():
    ''' Perimiterator scanner main thread. '''
    # Strip off any existing handlers that may have already been installed.
    logger = logging.getLogger()
    for handler in logger.handlers:
        logger.removeHandler(handler)

    # Reconfigure the root logger the way we want it.
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(process)d - [%(levelname)s] %(message)s'
    )

    # Get the account id for the current AWS account.
    account = perimeterator.helper.aws_account_id()
    logger.info("Running against AWS account %s", account)

    # Get configurable options from environment variables.
    input_queue = perimeterator.helper.sqs_arn_to_url(
        os.getenv("ENUMERATOR_SQS_QUEUE", None)
    )
    input_queue_region = os.getenv("ENUMERATOR_SQS_REGION", "us-west-2")
    logger.info(
        "Configured input queue is %s in %s",
        input_queue,
        input_queue_region,
    )

    output_queue = perimeterator.helper.sqs_arn_to_url(
        os.getenv("SCANNER_SQS_QUEUE", None)
    )
    output_queue_region = os.getenv("SCANNER_SQS_REGION", "us-west-2")
    logger.info(
        "Configured output queue is %s in %s",
        output_queue,
        output_queue_region,
    )

    # Setup clients for I/O.
    logger.info("Setting up input and output queue handlers (SQS)")
    _in = boto3.client("sqs", region_name=input_queue_region)
    _out = boto3.client("sqs", region_name=output_queue_region)

    # Kick off.
    logger.info("Starting message polling loop")
    while True:
        queue = _in.receive_message(
            QueueUrl=input_queue,
            WaitTimeSeconds=20,
        )
        try:
            messages = queue['Messages']
            logger.info(messages)
        except KeyError:
            logger.debug("No messages in queue, re-polling")
            continue


if __name__ == '__main__':
    main()
