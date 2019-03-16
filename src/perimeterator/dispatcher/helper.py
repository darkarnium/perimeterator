''' Perimeterator - Internal helpers for Dispatcher operations. '''


def sqs_arn_to_url(arn):
    ''' Convert an SQS ARN to SQS queue URL. '''
    arn_parts = arn.split(':')
    return 'https://sqs.{0}.amazonaws.com/{1}/{2}'.format(
        arn_parts[3],
        arn_parts[4],
        arn_parts[5],
    )
