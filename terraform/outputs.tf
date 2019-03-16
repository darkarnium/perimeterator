// Render the Enumerate SQS queue ARN and region to the user when Terraform
// has complete.
output "enumerator_sqs_queue" {
    value = "${aws_sqs_queue.enumerator.arn}"
}
output "enumerator_sqs_region" {
    value = "${var.deployment_region}"
}

// Render the Scanner SQS queue ARN and region to the user when Terraform
// has complete.
output "scanner_sqs_queue" {
    value = "${aws_sqs_queue.scanner.arn}"
}
output "scanner_sqs_region" {
    value = "${var.deployment_region}"
}

// Render the AWS Access Key Id to the user when Terraform has complete.
output "scanner_aws_access_key_id" {
    value = "${aws_iam_access_key.scanner.id}"
}

// Render the AWS Secret Access Key to the user when Terraform has complete.
output "scanner_aws_secret_access_key" {
    value = "${aws_iam_access_key.scanner.secret}"
}
