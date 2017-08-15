"""Defines SigMF exception classes."""


class SigMFError(Exception):
    """ SigMF base exception."""
    pass


class SigMFValidationError(SigMFError):
    """Exceptions related to validating SigMF metadata."""
    pass


class SigMFFileError(SigMFError):
    """Exceptions related to reading or writing SigMF archives."""
    pass
