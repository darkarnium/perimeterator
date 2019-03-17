''' Perimeterator - Port scanner (nmap). '''

import logging
import tempfile
import ipaddress
import subprocess

from perimeterator.scanner.exception import InvalidTargetException
from perimeterator.scanner.exception import UnhandledScanException
from perimeterator.scanner.exception import TimeoutScanException


def run(targets, timeout=300):
    ''' Runs a scan against the provided target(s). '''
    # Write IPs to a temporary file - which will be passed to nmap - and
    # validate that all provided target addresses are valid.
    with tempfile.NamedTemporaryFile(mode='w+') as fin:
        for target in targets:
            try:
                ipaddress.ip_address(target)
                fin.write(target)
                fin.write("\n")
            except ValueError as err:
                raise InvalidTargetException(err)

        # Seek back to the start of the file, and flush to disk.
        fin.flush()
        fin.seek(0)

        # Attempt to kick off the scan, and timebox the run.
        with tempfile.NamedTemporaryFile(mode='w+') as fout:
            try:
                # TODO: Expose ability to customise nmap arguments.
                subprocess.run(
                    [
                        "nmap",
                        "--privileged",     # Let nmap know it has caps.
                        "-iL", fin.name,    # Input hosts from file.
                        "-oX", fout.name,   # XML Output
                        "--no-stylesheet",  # Don't include XSL stylesheet.
                        "-T4",              # Set timing to "Normal".
                        "-Pn",              # Treat hosts as online.
                        "-sT",              # Connect() scan.
                        "-sU",              # UDP scan.
                    ],
                    check=True,
                    shell=False,
                    timeout=timeout,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except subprocess.CalledProcessError as err:
                raise UnhandledScanException(err)
            except subprocess.TimeoutExpired as err:
                raise TimeoutScanException(err)

            # Read back the file and return it to our caller.
            fout.seek(0)
            return fout.read()

