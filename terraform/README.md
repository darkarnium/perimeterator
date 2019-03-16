## Perimeterator - Terraform

## WARNING

Deployment of these Terraform configs will create AWS resources that will
incur cost! Please ensure you have familiarised yourself with the charges
associated with the created resources before deployment.

### Overview

This directory contains Terraform configs for deploying perimiterator. The
default configuration is as follows:

* Creation of SQS queue for scan requests.
* Creation of SQS queue for scan results.
* Creation of SQS dead-letter queue for errors.
* Creation of Lambda functions to enumerate AWS resources.
* Creation of IAM resources to allow Lambda functions to operate.
