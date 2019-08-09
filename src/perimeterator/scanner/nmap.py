''' Perimeterator - Port scanner (nmap). '''

import json
import tempfile
import ipaddress
import subprocess
import xml.etree.ElementTree as tree

from perimeterator.scanner.exception import InvalidTargetException
from perimeterator.scanner.exception import UnhandledScanException
from perimeterator.scanner.exception import TimeoutScanException


def _result_from_xml(xml, arn):
    ''' Converts Nmap XML format output to Perimeterator output format. '''
    root = tree.fromstring(xml)

    # Extract the scan arguments from the XML, and track as metadata.
    metadata = {
        "scanner": root.attrib["scanner"],
        "arguments": root.attrib["args"],
    }

    # Extract results from the scan and append to the results document.
    results = dict()

    for host in root.iter("host"):
        # Key results by address.
        address = host.find("address").attrib["addr"]
        results[address] = []

        # Append entries for ports not marked as 'closed'.
        for port in host.iter("port"):
            state = port.find("state").attrib["state"]
            if state != "closed":
                results[address].append({
                    "port": port.attrib["portid"],
                    "state": state,
                    "protocol": port.attrib["protocol"],
                })

    # Serialise to JSON before returning.
    return json.dumps({
        "metadata": metadata,
        "results": {
            arn: results
        }
    })


def run(arn, targets, timeout=300):
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
                        "-n",               # Don't resolve DNS.
                        "-T4",              # Set timing to "Normal".
                        "-Pn",              # Treat hosts as online.
                        "-sT",              # Connect() scan.
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

            # Read back the file from the start, convert to our required
            # output format, and return it to our caller.
            fout.seek(0)
            return _result_from_xml(fout.read(), arn)
