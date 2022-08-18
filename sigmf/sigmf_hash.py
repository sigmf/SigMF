# Copyright 2021 GNU Radio Foundation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
