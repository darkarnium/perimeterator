''' Perimeterator Scanner.

Provides scanning of resources identified by the Perimeterator Enumerator.
'''

import os
import logging
import perimeterator

import time


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
    while True:
        logger.info("Boop")
        time.sleep(5)


if __name__ == '__main__':
    main()
