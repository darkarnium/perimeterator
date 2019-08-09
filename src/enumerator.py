#!/usr/bin/env python3
''' Perimeterator Enumerator.

This wrapper is intended to allow for simplified AWS based deployment of the
Perimeterator enumerator. This allows for a cost effective method of
execution, as the Perimeterator poller component only needs to execute on a
defined schedule in order to detect changes.
'''

import os
import logging
import perimeterator

# TODO: This should likely be configurable.
MODULES = [
    'rds',
    'ec2',
    'elb',
    'elbv2',
    'es',
]


def lambda_handler(event, context):
    ''' An AWS Lambda wrapper for the Perimeterator enumerator. '''
    # Strip off any existing handlers that may have been installed by AWS.
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
    logger.info("Running in AWS account %s", account)

    # Get configurable options from environment variables.
    regions = os.getenv("ENUMERATOR_REGIONS", "us-west-2").split(",")
    sqs_queue = os.getenv("ENUMERATOR_SQS_QUEUE", None)
    logger.info("Configured results SQS queue is %s", sqs_queue)
    logger.info(
        "Configured regions for resource enumeration are %s",
        ", ".join(regions)
    )

    # Setup the SQS dispatcher for submission of addresses to scanners.
    queue = perimeterator.dispatcher.sqs.Dispatcher(queue=sqs_queue)

    # Process regions one at a time, enumerating addresses for all configured
    # resources in the given region. Currently, it's not possible to only
    # enumerate different resources types by region. Maybe later! :)
    for region in regions:
        logger.info("Attempting to enumerate resources in %s", region)

        for module in MODULES:
            logger.info("Attempting to enumerate %s resources", module)
            try:
                # Ensure a handler exists for this type of resource.
                hndl = getattr(perimeterator.enumerator, module).Enumerator(
                    region=region
                )
            except AttributeError as err:
                logger.error(
                    "Handler for %s resources not found, skipping: %s",
                    module,
                    err
                )
                continue

            # Get all addresses and dispatch to SQS for processing.
            logger.info(
                "Submitting %s resources in %s for processing",
                module,
                region
            )
            queue.dispatch(account, hndl.get())


if __name__ == '__main__':
    ''' Allow the script to be invoked outside of Lambda. '''
    lambda_handler(
        dict(),  # No real 'event' data.
        dict()   # No real 'context' data.
    )
