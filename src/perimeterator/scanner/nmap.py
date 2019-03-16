''' Perimeterator - Port scanner (nmap). '''

import subprocess
import logging


class Scanner(object):
    ''' Perimeterator - Port scanner (nmap). '''

    def __init__(self, region):
        self.logger = logging.getLogger(__name__)
