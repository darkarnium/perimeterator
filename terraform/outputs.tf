// Render the Enumerate SQS queue ARN and region to the user when Terraform
// has complete.
output "ENUMERATOR_SQS_QUEUE" {
    value = "${aws_sqs_queue.enumerator.arn}"
}

// Render the Scanner SQS queue ARN and region to the user when Terraform
// has complete.
output "SCANNER_SQS_QUEUE" {
    value = "${aws_sqs_queue.scanner.arn}"
}

// Render the AWS Access Key Id to the user when Terraform has complete.
output "AWS_ACCESS_KEY_ID" {
    value = "${aws_iam_access_key.scanner.id}"
}

// Render the AWS Secret Access Key to the user when Terraform has complete.
output "AWS_SECRET_ACCESS_KEY" {
    value = "${aws_iam_access_key.scanner.secret}"
}
