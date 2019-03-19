''' Perimeterator - Internal helpers for Enumerator operations. '''

import boto3
import socket


def aws_elb_arn(region, name):
    ''' Constructs an ARN for an ELB in the given region. '''
    return 'arn:aws:elasticloadbalancing:{0}:{1}:loadbalancer/{2}'.format(
        region,
        aws_account_id(),
        name,
    )


def aws_ec2_arn(region, identifier, resource='instance'):
    ''' Constructs an ARN for an EC2 resource in the given region. '''
    return 'arn:aws:ec2:{0}:{1}:{2}/{3}'.format(
        region,
        aws_account_id(),
        resource,
        identifier,
    )


def dns_lookup(fqdn):
    ''' Lookups up the given FQDN returning an array of IPs. '''
    addresses = []
    try:
        # Provide a port number as '0' as we only want to trigger a DNS
        # lookup, no more, no less.
        for info in socket.getaddrinfo(fqdn, 0):
            addresses.append(info[4][0])
    except socket.gaierror:
        # This is super janky, but hey.
        pass

    # Convert to a set and back again to deduplicate.
    return list(set(addresses))


def aws_sqs_queue_url(arn):
    ''' Convert an SQS ARN to SQS queue URL. '''
    client = boto3.client('sqs')
    queue = client.get_queue_url(
        QueueName=arn.split(':')[-1],
        QueueOwnerAWSAccountId=arn.split(':')[-2],
    )
    return queue['QueueUrl']


def aws_account_id():
    ''' Attempts to get the account id for the current AWS account. '''
    client = boto3.client('sts')
    return client.get_caller_identity()["Account"]
