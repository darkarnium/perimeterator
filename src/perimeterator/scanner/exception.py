''' Perimeterator - Scanner exceptions. '''


class ScannerException(Exception):
    ''' Base exception for scanners. '''


class InvalidTargetException(ScannerException):
    ''' A target provided to a scanner was not valid. '''


class UnhandledScanException(ScannerException):
    ''' Something went wrong with the scan. '''


class TimeoutScanException(ScannerException):
    ''' The scan took too long, and was killed. '''
