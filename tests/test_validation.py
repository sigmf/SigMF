# Copyright 2016 GNU Radio Foundation
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

import tempfile

import sigmf
from sigmf import SigMFFile

from .testdata import TEST_FLOAT32_DATA, TEST_METADATA


def test_valid_data():
    assert SigMFFile(TEST_METADATA).validate()


def test_invalid_capture_sequence():
    '''metadata must have captures in order'''
    invalid_metadata = dict(TEST_METADATA)
    invalid_metadata[SigMFFile.CAPTURE_KEY] = [
        {
            SigMFFile.START_INDEX_KEY: 10
        },
        {
            SigMFFile.START_INDEX_KEY: 9
        }
    ]
    assert not SigMFFile(invalid_metadata).validate()


def test_invalid_annotation_sequence():
    '''metadata must have annotations in order'''
    invalid_metadata = dict(TEST_METADATA)
    invalid_metadata[SigMFFile.ANNOTATION_KEY] = [
        {
            SigMFFile.START_INDEX_KEY: 2,
            SigMFFile.LENGTH_INDEX_KEY: 120000,
            SigMFFile.COMMENT_KEY: "stuff"
        },
        {
            SigMFFile.START_INDEX_KEY: 1,
            SigMFFile.LENGTH_INDEX_KEY: 120000,
            SigMFFile.COMMENT_KEY: "stuff"
        }
    ]
    assert not SigMFFile(invalid_metadata).validate()


def test_invalid_hash():
    '''metadata must have captures in order'''
    invalid_metadata = dict(TEST_METADATA)
    invalid_metadata[SigMFFile.GLOBAL_KEY][SigMFFile.HASH_KEY] = 'derp'
    temp_path = tempfile.mkstemp()[1]
    TEST_FLOAT32_DATA.tofile(temp_path)
    try:
        SigMFFile(metadata=invalid_metadata, data_file=temp_path)
    except sigmf.error.SigMFFileError:
        # this should occur since the hash is wrong
        pass
    else:
        # this only happens if no error occurs
        assert False
