# Copyright: Multiple Authors
#
# This file is part of SigMF. https://github.com/gnuradio/SigMF
#
# SPDX-License-Identifier: LGPL-3.0-or-later

'''Hashing Functions'''

import hashlib
import os


def calculate_sha512(filename=None, fileobj=None, offset_and_size=None):
    """
    Return sha512 of file or fileobj.
    """
    the_hash = hashlib.sha512()
    if filename is not None:
        fileobj = open(filename, "rb")
    if offset_and_size is None:
        bytes_to_hash = os.path.getsize(filename)
    else:
        fileobj.seek(offset_and_size[0])
        bytes_to_hash = offset_and_size[1]
    bytes_read = 0
    while bytes_read < bytes_to_hash:
        buff = fileobj.read(min(4096, (bytes_to_hash - bytes_read)))
        the_hash.update(buff)
        bytes_read += len(buff)
    if filename is not None:
        fileobj.close()
    return the_hash.hexdigest()
