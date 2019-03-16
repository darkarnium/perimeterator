''' Implements tests for Dispatcher helpers. '''

import unittest

import perimeterator


class DispatcherHelperTestCase(unittest.TestCase):
    ''' Implements tests for Dispatcher helpers. '''

    def test_sqs_arn_to_url(self):
        ''' Ensure that the conversion between SQS ARN and URL works. '''
        canididate = 'arn:aws:sqs:us-west-2:12345678:abcdef'
        expected = 'https://sqs.us-west-2.amazonaws.com/12345678/abcdef'
        self.assertEquals(
            perimeterator.dispatcher.helper.sqs_arn_to_url(canididate),
            expected,
        )
