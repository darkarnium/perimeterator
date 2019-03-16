''' Perimeterator Poller.

This wrapper is intended to allow for simplified AWS based deployment of the
Perimeterator poller. This allows for a cost effective method of execution,
as the Perimeterator poller component only needs to execute on a defined
schedule in order to detect changes.
'''

import logging
import perimeterator

# Move this into configuration once well tested.
REGIONS = [
    'us-west-2',
]

MODULES = [
    'ec2',
    'elb',
    'elbv2',
]

SQS_REGION = 'us-west-2'
SQS_QUEUE = 'https://sqs.us-west-2.amazonaws.com/639646276157/perimiterator-scanner'


def lambda_handler(event, context):
    ''' An AWS Lambda wrapper for the Perimeterator poller. '''
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(process)d - [%(levelname)s] %(message)s'
    )
    logger = logging.getLogger(__name__)

    # Get the account id for the current AWS account.
    account = perimeterator.enumerator.helper.aws_account_id()
    logger.info("AWS account id %s", account)

    # Setup the SQS dispatcher for submission of addresses to scanners.
    queue = perimeterator.dispatcher.sqs.Dispatcher(
        region=SQS_REGION,
        queue=SQS_QUEUE,
    )

    # Process regions one at a time, enumerating addresses for all configured
    # resources in the given region. Currently, it's not possible to only
    # enumerate different resources types by region. Maybe later! :)
    for region in REGIONS:
        logger.info("Attempting to enumerate resources in %s", region)

        for module in MODULES:
            logger.info("Attempting to enumerate %s resources", module)
            try:
                # Ensure a handler exists for this type of resource.
                hndl = getattr(perimeterator.enumerator, module).Enumerator(
                    region=region,
                )
            except AttributeError as err:
                logger.error(
                    "Handler for %s resources not found, skipping: %s",
                    module,
                    err,
                )
                continue

            # Get all addresses and dispatch to SQS for processing.
            logger.info(
                "Submitting %s resources in %s for processing",
                module,
                region,
            )
            queue.dispatch(region, account, hndl.get())


if __name__ == '__main__':
    ''' Allow the script to be invoked outside of Lambda. '''
    lambda_handler(
        dict(),  # No real 'event' data.
        dict()   # No real 'context' data.
    )
