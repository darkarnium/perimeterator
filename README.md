## Perimeterator

'Continuous' AWS perimeter monitoring - Periodically scan internet facing AWS
resources to detect misconfigured services.

### Overview

Perimiterator is a small project intended to allow for continuous auditing
of internet facing AWS services. It can be quickly deployed into AWS and will
periodically enumerate internet-facing IP addresses for a number of commonly
misconfigured AWS resources.

The results from this enumeration process are pushed into a work queue for
scanning by external monitoring workers in order to locate open network
services.

Monitoring workers can be deployed anywhere, and are intended to be deployed
into non-trusted networks in order to provide a representation of access to
services from the "general internet".

Currently, the following AWS resource types are supported:

* EC2
* ELB
* ELBv2
* RDS

### Deployment

Perimiterator requires a few components in order to function. However, in
order to make getting started as easy as possible, some Terraform configs
have been provided inside of the `terraform/` directory.

To get started, please see the `terraform/README.md` file.

### Components

Perimiterator has a number of components, due to its distributed nature. A
brief overview of each of these components has been provided below.

#### Enumerator (`enumerator.py`)

This component is responsible for enumerating internet facing IP addresses
which will be passed to downstream monitoring workers for scanning. This
is intended to be run in Lambda, or somewhere inside of AWS which has access
to perform the required 'Describe' operations.

As this is intended to be run in Lambda, configuration is currently only
possible through environment variables. A brief summary of these exposed
variables is as follows:

* `ENUMERATOR_REGIONS`
  * A comma-delimited list of AWS regions to enumerate resources from.
  * This is set automatically if the provided Terraform configs are used.
* `ENUMERATOR_SQS_REGION`
  * The region in which the SQS scan queue was created in.
  * This is set automatically if the provided Terraform configs are used.
* `ENUMERATOR_SQS_QUEUE`
  * The URL of the SQS scan queue.
  * This is created automatically if the provided Terraform configs are used.
