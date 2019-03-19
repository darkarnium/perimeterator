#!/usr/bin/env python3
''' Perimeterator Scanner - Scan resources identified by the Enumerator. '''

import os
import json
import boto3
import logging

import perimeterator

# TODO: Move this to configuration.
SCAN_TIMEOUT = 500


def main():
    ''' perimeterator scanner main thread. '''
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
    input_queue = perimeterator.helper.aws_sqs_queue_url(
        os.getenv("ENUMERATOR_SQS_QUEUE", None)
    )
    output_queue = perimeterator.helper.aws_sqs_queue_url(
        os.getenv("SCANNER_SQS_QUEUE", None)
    )
    logger.info("Configured input queue is %s", input_queue)
    logger.info("Configured output queue is %s", output_queue)

    # Setup I/O queues and start processing.
    sqs = boto3.client("sqs")

    logger.info("Starting message polling loop")
    while True:
        # Only process ONE message at a time, as parallelising the scan
        # operations is likely in larger environments. Further to this, set
        # the visibility timeout to the SCAN_TIMEOUT plus 15 seconds to
        # prevent a message from being 'requeued' / unhidden before a scan
        # has had time to complete - or timeout.
        queue = sqs.receive_message(
            QueueUrl=input_queue,
            WaitTimeSeconds=20,
            VisibilityTimeout=(SCAN_TIMEOUT + 15),
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
                    resource,
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
            response = sqs.send_message(
                QueueUrl=output_queue,
                MessageAttributes=messages[i]['MessageAttributes'],
                MessageBody=scan_result,
            )
            logger.info(
                "Enqueued scan results for resource %s as %s",
                resource,
                response["MessageId"],
            )

            # Delete the processed message.
            logger.info("[%s] Message processed successfully", message_id)
            sqs.delete_message(
                QueueUrl=input_queue,
                ReceiptHandle=handle,
            )


if __name__ == '__main__':
    main()
