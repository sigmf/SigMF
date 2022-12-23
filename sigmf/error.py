# Copyright: Multiple Authors
#
# This file is part of SigMF. https://github.com/gnuradio/SigMF
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Defines SigMF exception classes."""


class SigMFError(Exception):
    """ SigMF base exception."""
    pass


class SigMFValidationError(SigMFError):
    """Exceptions related to validating SigMF metadata."""
    pass


class SigMFAccessError(SigMFError):
    """Exceptions related to accessing the contents of SigMF metadata, notably
    when expected fields are missing or accessing out of bounds captures."""
    pass


class SigMFFileError(SigMFError):
    """Exceptions related to reading or writing SigMF files or archives."""
    pass
