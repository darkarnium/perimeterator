## Perimeterator - Terraform

## WARNING

Deployment of these Terraform configs will create AWS resources that will
incur cost! Please ensure you have familiarised yourself with the charges
associated with the created resources before deployment.

### Overview

This directory contains Terraform configs for deploying perimeterator. The
default configuration is as follows:

* Creation of SQS queue for scan requests.
* Creation of SQS queue for scan results.
* Creation of SQS dead-letter queue for errors.
* Creation of Lambda functions to enumerate AWS resources.
* Creation of IAM resources to allow Lambda functions to operate.

### Deployment

To deploy simply follow the following steps:

1. `git clone` this repository to your machine.
2. Ensure AWS keys with the required permissions [are configured](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html#cli-quick-configuration).
3. Ensure [Terraform](https://learn.hashicorp.com/terraform/getting-started/install.html) is installed.
4. Change into the `terraform/` directory.
5. Execute `terraform plan`.
6. When ready to deploy, execute `terraform apply`.
7. Enjoy your ☕️ / 🍺 / 🥃 / 🍚 while you wait for the deployment to finish.
