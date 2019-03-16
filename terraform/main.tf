
// Deployment will be into AWS. Leave Terraform to locate credentials via
// usual AWS SDK methods - environment variables, configuration files, or
// instance roles, etc.
provider "aws" {
  region = "${var.deployment_region}"
}

// Zip up the `src` directory, to produce a Lambda compatible deployment
// artifact. Code that runs in Lambda only requires boto3, which is installed
// by default so there is no need to include setup.py and co.
data "archive_file" "deployment" {
  type        = "zip"
  output_path = "${path.module}/perimiterator.zip"
  source_dir  = "${path.module}/../src/"
}

// Create a Perimiterator dead letter queue.
resource "aws_sqs_queue" "deadletter" {
  name                      = "perimiterator-deadletter"
  message_retention_seconds = 86400
  max_message_size          = 1024
}

// Create a Perimiterator scan queue.
resource "aws_sqs_queue" "scan" {
  name                      = "perimiterator-scan"
  message_retention_seconds = 3600
  max_message_size          = 1024
  redrive_policy            = <<EOF
{
  "deadLetterTargetArn": "${aws_sqs_queue.deadletter.arn}",
  "maxReceiveCount": 4
}
EOF
}

// Create a role for the Lambda function(s) to use.
resource "aws_iam_role" "enumerator" {
  name = "perimiterator-enumerator"
  path = "/"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

// Create a CloudWatch log group for Lambda logs.
resource "aws_cloudwatch_log_group" "enumerator" {
  name              = "/aws/lambda/perimiterator-enumerator"
  retention_in_days = 14
}

// Create a policy to allow the Lambda function to log output to CloudWatch.
resource "aws_iam_policy" "log" {
  name        = "perimiterator-enumerator-log"
  description = "IAM policy for Perimiterator Enumerator (Logging)"
  policy      = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "${aws_cloudwatch_log_group.enumerator.arn}",
      "Effect": "Allow"
    }
  ]
}
EOF
}

// Create a policy to allow the Lambda function to enqueue messages onto the
// scan queue.
resource "aws_iam_policy" "enqueue" {
  name        = "perimiterator-enumerator-enqueue"
  description = "IAM policy for Perimiterator Enumerator (Enqueue)"
  policy      = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sqs:SendMessage"
      ],
      "Resource": "${aws_sqs_queue.scan.arn}"
    }
  ]
}
EOF
}

// Create a policy to allow the Lambda function to describe various AWS 
// resources.
resource "aws_iam_policy" "describe" {
  name        = "perimiterator-enumerator-describe"
  description = "IAM policy for Perimiterator Enumerator (Describe)"
  policy      = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "ec2:DescribeInstances",
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "elasticloadbalancing:DescribeLoadBalancers",
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "rds:DescribeDBInstances",
      "Resource": "*"
    }
  ]
}
EOF
}

// Bolt created policies onto the created IAM role.
resource "aws_iam_role_policy_attachment" "log" {
  role       = "${aws_iam_role.enumerator.name}"
  policy_arn = "${aws_iam_policy.log.arn}"
}
resource "aws_iam_role_policy_attachment" "describe" {
  role       = "${aws_iam_role.enumerator.name}"
  policy_arn = "${aws_iam_policy.describe.arn}"
}
resource "aws_iam_role_policy_attachment" "enqueue" {
  role       = "${aws_iam_role.enumerator.name}"
  policy_arn = "${aws_iam_policy.enqueue.arn}"
}

// Deploy the Enumerator Lambda function.
resource "aws_lambda_function" "perimiterator_enumerator" {
  role             = "${aws_iam_role.enumerator.arn}"
  runtime          = "python3.7"
  timeout          = "${var.lambda_enumerator_timeout}"
  memory_size      = "${var.lambda_enumerator_memory_size}"

  handler          = "enumerator.lambda_handler"
  filename         = "perimiterator.zip"
  function_name    = "perimiterator-enumerator"
  source_code_hash = "${data.archive_file.deployment.output_base64sha256}"

  // Configuration of function is through environment variables.
  environment {
    variables = {
      ENUMERATOR_REGIONS    = "${join(",", var.enumerator_regions)}"
      ENUMERATOR_SQS_QUEUE  = "${aws_sqs_queue.scan.arn}"
      ENUMERATOR_SQS_REGION = "${var.deployment_region}"
    }
  }
}
