
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
  output_path = "${path.module}/perimeterator.zip"
  source_dir  = "${path.module}/../src/"
}

// Create a perimeterator dead letter queue.
resource "aws_sqs_queue" "deadletter" {
  name                      = "perimeterator-deadletter"
  message_retention_seconds = 86400
  max_message_size          = 1024
}

// Create a perimeterator enumerator queue.
resource "aws_sqs_queue" "enumerator" {
  name                      = "perimeterator-enumerator"
  message_retention_seconds = 3600
  max_message_size          = 1024
  redrive_policy            = <<EOF
{
  "deadLetterTargetArn": "${aws_sqs_queue.deadletter.arn}",
  "maxReceiveCount": 4
}
EOF
}

// Create a perimeterator scanner queue.
resource "aws_sqs_queue" "scanner" {
  name                      = "perimeterator-scanner"
  message_retention_seconds = 3600
  max_message_size          = 102400
  redrive_policy            = <<EOF
{
  "deadLetterTargetArn": "${aws_sqs_queue.deadletter.arn}",
  "maxReceiveCount": 4
}
EOF
}

// Create an IAM user for external scanning.
resource "aws_iam_user" "scanner" {
  name = "perimeterator-scanner"
}

// Create the IAM access key for the scanner user.
resource "aws_iam_access_key" "scanner" {
  user = "${aws_iam_user.scanner.name}"
}

// Create a policy for the scanner user to access required queues. This 
// allows the scanners to receive messages from the Enumerator, and allows
// them to send messages to the results queue.
resource "aws_iam_user_policy" "scanner" {
  name   = "perimeterator-scanner"
  user   = "${aws_iam_user.scanner.name}"
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sqs:DeleteMessage",
        "sqs:GetQueueUrl",
        "sqs:ReceiveMessage"
      ],
      "Resource": [
        "${aws_sqs_queue.enumerator.arn}"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "sqs:GetQueueUrl",
        "sqs:SendMessage"
      ],
      "Resource": "${aws_sqs_queue.scanner.arn}"
    }
  ]
}
EOF
}

// Create a role for the Lambda function(s) to use.
resource "aws_iam_role" "enumerator" {
  name = "perimeterator-enumerator"
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
  name              = "/aws/lambda/perimeterator-enumerator"
  retention_in_days = 14
}

// Create a policy to allow the Lambda function to log output to CloudWatch.
resource "aws_iam_policy" "log" {
  name        = "perimeterator-enumerator-log"
  description = "IAM policy for perimeterator Enumerator (Logging)"
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
  name        = "perimeterator-enumerator-enqueue"
  description = "IAM policy for perimeterator Enumerator (Enqueue)"
  policy      = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sqs:SendMessage",
        "sqs:GetQueueUrl"
      ],
      "Resource": "${aws_sqs_queue.enumerator.arn}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sqs:GetQueueUrl"
      ],
      "Resource": "${aws_sqs_queue.scanner.arn}"
    }
  ]
}
EOF
}

// Create a policy to allow the Lambda function to describe various AWS 
// resources.
resource "aws_iam_policy" "describe" {
  name        = "perimeterator-enumerator-describe"
  description = "IAM policy for perimeterator Enumerator (Describe)"
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
    },
    {
      "Effect": "Allow",
      "Action": "es:ListDomainNames",
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "es:DescribeElasticsearchDomain",
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
resource "aws_lambda_function" "enumerator" {
  role             = "${aws_iam_role.enumerator.arn}"
  runtime          = "python3.7"
  timeout          = "${var.lambda_enumerator_timeout}"
  memory_size      = "${var.lambda_enumerator_memory_size}"

  handler          = "enumerator.lambda_handler"
  filename         = "perimeterator.zip"
  function_name    = "perimeterator-enumerator"
  source_code_hash = "${data.archive_file.deployment.output_base64sha256}"

  // Configuration of function is through environment variables.
  environment {
    variables = {
      ENUMERATOR_REGIONS    = "${join(",", var.enumerator_regions)}"
      ENUMERATOR_SQS_QUEUE  = "${aws_sqs_queue.enumerator.arn}"
      ENUMERATOR_SQS_REGION = "${var.deployment_region}"
    }
  }
}

// Create the CloudWatch rule to invoke this function every N hours.
resource "aws_cloudwatch_event_rule" "invoker" {
  name                = "perimeterator-invoker"
  description         = "Invokes Perimeterator Enumerator on the configured schedule"
  schedule_expression = "${var.enumerator_schedule}"
}

resource "aws_cloudwatch_event_target" "invoker" {
  target_id = "perimeterator-invoker"
  rule      = "${aws_cloudwatch_event_rule.invoker.name}"
  arn       = "${aws_lambda_function.enumerator.arn}"
}

// Allow CloudWatch to invoke the function.
resource "aws_lambda_permission" "invoker" {
  action        = "lambda:InvokeFunction"
  principal     = "events.amazonaws.com"
  statement_id  = "AllowExecutionFromCloudWatch"
  function_name = "${aws_lambda_function.enumerator.function_name}"
}
