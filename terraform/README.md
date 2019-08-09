# Perimeterator - Terraform

This directory contains a set of Terraform configs which will deploy
Perimeterator to AWS, and trigger the first "Enumeration" run. It will also
schedule an "Enumeration" run to automatically take place every 24-hours.

## WARNING

Deployment of these Terraform configs will create AWS resources that will
incur cost! Please ensure you have familiarised yourself with the charges
associated with the created resources before deployment.

In addition to this, an IAM user for use with scanners external to AWS will
be created as part of this deployment. The secret and access keys for this
user are written to the `tfstate` file by Terraform. Please ensure to protect
this state file appropriately, if required.

Finally, **the author accepts no responsibility for errors and omissions in
these Terraform configs which may yield unexpected behaviour and / or
security misconfiguration.** 

## Overview

This directory contains Terraform configs for deploying Perimeterator. A
non-exhaustive list of created resources is as follows:

* Creation of SQS queue for scan requests (`enumerate`).
* Creation of SQS queue for scan results (`scanner`).
* Creation of SQS dead-letter queue for errors (`deadletter`).
* Creation of Lambda functions to enumerate AWS resources.
* Creation of IAM resources to allow Lambda functions to operate.
* Creation of an IAM user for "external" scanners.
* Creation of IAM keys for the created scanners.
* Creation of IAM resources to allow "external" scanners functions to operate.
* Creation of a CloudWatch Log Group for logging the output of Enumerator runs.

## Deployment

To deploy simply follow the following steps:

1. `git clone` this repository to your machine.
2. Ensure AWS keys with the required permissions [are configured](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html#cli-quick-configuration).
3. Ensure [Terraform](https://learn.hashicorp.com/terraform/getting-started/install.html) is installed.
4. Change into the `terraform/` directory.
5. Execute `terraform plan`.
6. When ready to deploy, execute `terraform apply`.
7. Enjoy your ☕️ / 🍺 / 🥃 / 🍚 while you wait for the deployment to finish.
8. Use the output AWS IAM keys to deploy a scanner.

Please be aware that the deployed `enumerator` Lambda function will only
execute every 24 hours by default, and it may take some time for the first
run to be triggered by the CloudWatch Events rule. Logs can be found in the
CloudWatch console which can be used to monitor the status of `enumerator`
runs.

Invocation can also be performed manually after - if required - with the
following AWS CLI command:

```
aws lambda invoke --function-name perimeterator-enumerator /dev/null
```

## Logs

When deployed, a new log group called `perimeterator-enumerator` will be
created in CloudWatch. Logs of Enumerator runs can be found in this log
group, easily accessible from CloudWatch Logs in the AWS console.

## Customisation

In order to customise the deployment - such as changing the frequency of the
Enumerator run, or region(s) on which it will enumerate resources - please
see the `variables.tf` file, and the comments associated with the respective
variable you would like to change.
