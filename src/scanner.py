#!/usr/bin/env python3
''' Perimeterator Scanner - Scan resources identified by the Enumerator. '''

import os
import json
import boto3
import logging

import perimeterator

# TODO: Move this to configuration.
SCAN_TIMEOUT = 300


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

    logger.info("Starting message polling loop")
    while True:
        # Only process ONE message at a time, as parallelising the scan
        # operations is likely in larger environments. Further to this, set
        # the visibility timeout to the SCAN_TIMEOUT plus 30 seconds to
        # prevent a message from being 'requeued' / unhidden before a scan
        # has had time to complete - or timeout.
        queue = _in.receive_message(
            QueueUrl=input_queue,
            WaitTimeSeconds=20,
            VisibilityTimeout=(SCAN_TIMEOUT + 30),
            MaxNumberOfMessages=1,
            MessageAttributeNames=["All"],
        )
        try:
            messages = queue['Messages']
        except KeyError:
            logger.debug("No messages in queue, re-polling")
            continue

        # Process messages, and kick off scan(s).
        # TODO: Fan-out via multiprocess to perform parallel scans?
        logger.info("Got %d messages from the queue", len(messages))
        for i in range(0, len(messages)):
            # Ensure require attributes exist.
            try:
                handle = messages[i]['ReceiptHandle']
                resource = messages[i]['MessageAttributes']['Identifier']['StringValue']
                message_id = messages[i]['MessageId']
            except KeyError as err:
                logger.error(
                    "[%s] Required message attributes are missing: %s",
                    message_id,
                    err
                )
                continue

            # Extract IPs from the message, and initiate scan.
            logger.info("[%s] Processing message body", message_id)
            try:
                targets = json.loads(messages[i]["Body"])
            except json.decoder.JSONDecodeError as err:
                logger.error(
                    "[%s] Message body appears malformed: %s",
                    message_id,
                    err,
                )
                continue

            # Start the scan, and timebox it.
            try:
                logger.info(
                    "[%s] Starting scan of resource %s",
                    message_id,
                    resource,
                )
                scan_result = perimeterator.scanner.nmap.run(
                    targets,
                    timeout=SCAN_TIMEOUT,
                )
            except perimeterator.scanner.exception.TimeoutScanException:
                logger.error(
                    "[%s] Scan timed out after %d seconds",
                    message_id,
                    SCAN_TIMEOUT,
                )
                continue
            except perimeterator.scanner.exception.ScannerException as err:
                logger.error(
                    "[%s] A scanner exception was encountered: %s",
                    message_id,
                    err,
                )
                continue

            # Submit the results.
            # TODO: Dry move this into dispatcher and genericise.
            # TODO: Build a common output format for different scan modules?
            response = _out.send_message(
                QueueUrl=output_queue,
                MessageAttributes=messages[i]['MessageAttributes'],
                MessageBody=json.dumps({
                    "result": scan_result,
                })
            )
            logger.info(
                "Enqueued scan results for resource %s as %s",
                resource,
                response["MessageId"],
            )

            # Delete the processed message.
            logger.info("[%s] Message processed successfully", message_id)
            _in.delete_message(
                QueueUrl=input_queue,
                ReceiptHandle=handle,
            )

if __name__ == '__main__':
    main()
