// Defines which region the Lambda functions will be deployed into.
variable deployment_region {
    default = "us-west-2"
}

// The schedule on which to trigger the Enumerator.
variable enumerator_schedule {
    default = "rate(24 hours)"
}

// A list of regions the Perimeterator Enumerator will scan.
variable enumerator_regions {
    type    = "list"
    default = [
        "us-west-2",
        "us-west-1",
        "us-east-2",
        "us-east-1",
        "sa-east-1",
        "eu-west-3",
        "eu-west-2",
        "eu-west-1",
        "eu-north-1",
        "eu-central-1",
        "ca-central-1",
        "ap-southeast-2",
        "ap-southeast-1",
        "ap-south-1",
        "ap-northeast-2",
        "ap-northeast-1",
    ]
}

// The maximum amount of memory to allow the enumerator Lambda function to
// consume.
variable lambda_enumerator_memory_size {
    default = "256"
}

// The maximum duration that the enumerator Lambda function can run (timeout).
variable lambda_enumerator_timeout {
    default = "300"
}
