![Perimeterator](./docs/images/Perimeterator.png?raw=true)


Perimeterator is a small project intended to allow for continuous auditing
of internet facing AWS services. It can be quickly deployed into AWS and will
periodically enumerate internet-facing IP addresses for a number of commonly
misconfigured AWS resources.

The results from this enumeration process are pushed into a work queue for
scanning by external scanner 'workers' in order to locate open network
services. Scanner 'workers' can be deployed anywhere, and are intended to be
deployed into non-trusted networks in order to provide a representation of
access to services from the "general internet".

Currently, the following AWS resource types are supported:

* EC2
* ELB
* ELBv2
* RDS
* ES

All communication between Perimeterator components occurs asynchronously
through the use of AWS SQS queues.

![Architecture](./docs/images/Architecture.png?raw=true)

## Demo

[![asciicast](https://asciinema.org/a/234948.svg)](https://asciinema.org/a/234948)

## Getting Started / Deployment

Perimeterator requires a few components in order to function. However, in
order to make getting started as easy as possible, a number of Terraform
configs have been provided inside of the `terraform/` directory.

To get started, please see the `terraform/README.md` file.

## Components

Perimeterator has a number of components, due to its distributed nature. A
brief overview of each of these components has been provided below.

### Enumerator (`enumerator.py`)

This component is responsible for enumerating internet facing IP addresses
which will be passed to downstream monitoring workers for scanning. This
is intended to be run in Lambda, or somewhere inside of AWS which has access
to perform the required "Describe" operations.

As this is intended to be run in Lambda, configuration is currently only
possible through environment variables. A brief summary of these exposed
variables is as follows:

* `ENUMERATOR_REGIONS`
  * A comma-delimited list of AWS regions to enumerate resources from.
  * This is set automatically if the provided Terraform configs are used.
* `ENUMERATOR_SQS_QUEUE`
  * The URL of the SQS scan queue.
  * This is created automatically if the provided Terraform configs are used.

### Scanner (`scanner.py`)

This component is responsible for performing scanning of the IPs enumerated
by the Enumerator. This component should be run from an "untrusted" network
in order to gain a better insight into exposure from the perspective of the
"general internet".

Currently, the Scanner only uses `nmap` with the [default `nmap-services`](https://nmap.org/book/man-port-specification.html)
provided port range for TCP/UDP services. This is in order to prevent scans
from taking an extremely long time to complete per host, at the cost of some
accuracy in the case where uncommon ports are in use. This is likely to be
made user configurable in the near future.

An example `Dockerfile` for this component can be found in the root of this
repository. As this component is likely not running inside of AWS, an IAM user
and associated Access Key and Secret Key is created automatically for you if
using the included Terraform configs for deployment.

The following configuration is required to operate correctly. Once again,
configuration is only possible through environment variables. A brief summary
of these variables is as follows:

* `AWS_DEFAULT_REGION`
  * The default AWS region to interact with.
  * This is set by default to `us-west-2`.
* `AWS_ACCESS_KEY_ID`
  * The AWS access key associated with a user able to interact with SQS.
  * This is created automatically if the provided Terraform configs are used.
* `AWS_SECRET_ACCESS_KEY`
  * The AWS secret key associated with a user able to interact with SQS.
  * This is created automatically if the provided Terraform configs are used.
* `ENUMERATOR_SQS_QUEUE`
  * The URL of the SQS scan queue (input).
  * This is created automatically if the provided Terraform configs are used.
* `SCANNER_SQS_QUEUE`
  * The URL of the SQS results queue (output).
  * This is created automatically if the provided Terraform configs are used.

Building and executing this container can be performed by executing the
following. Of course, the blank fields will need to be populated with the
appropriate values. However, these match the names of the `outputs` from
Terraform if Perimeterator is deployed using the provided Terraform configs.

```
docker build -t perimeterator-scanner:master .
docker run \
    -e AWS_ACCESS_KEY_ID= \
    -e AWS_SECRET_ACCESS_KEY= \
    -e SCANNER_SQS_QUEUE= \
    -e ENUMERATOR_SQS_QUEUE= \
    perimeterator-scanner:master
```

### Notify (`notify.py`)

This component is in progress, but is not yet complete.

## Results

Result data from scans is currently written to an SQS queue ready for
downstream processing. Fetching and processing this data is still left as an
"exercise for the reader", however, a reporting mechanism which consumes this
data and generates a "diff" of results is actively being worked on.

The format of the output data, currently, is as follows:

```
{
    "metadata": {
        "scanner": "nmap",
        "arguments": "-Pn -sT -sU -T4 -n",
    },
    "results": {
        "arn:aws:ec2:12345678:instance/i-coffee": {
            "192.0.2.0": [
                {
                    "port": "22",
                    "state": "open",
                    "protocol": "tcp"
                },
                {
                    "port": "80",
                    "state": "open",
                    "protocol": "tcp"
                }
            ]
        }
    }
}
```

Further to this, and if required, the ARN of the resource from which the
scanned address was found is present in the SQS message attributes as a
string value named `Identifier`.
