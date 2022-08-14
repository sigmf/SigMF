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
import unittest

import sigmf
from sigmf import SigMFFile

from jsonschema.exceptions import ValidationError

from .testdata import TEST_FLOAT32_DATA, TEST_METADATA


def test_valid_data():
    '''assure the supplied metadata is OK'''
    invalid_metadata = dict(TEST_METADATA)
    SigMFFile(TEST_METADATA).validate()

class FailingCases(unittest.TestCase):
    '''Cases where the validator should throw an exception.'''
    def setUp(self):
        self.metadata = dict(TEST_METADATA)

    def test_extra_top_level_key(self):
        '''no extra keys allowed on the top level'''
        self.metadata['extra'] = 0
        with self.assertRaises(ValidationError):
            SigMFFile(self.metadata).validate()

    def test_extra_top_level_key(self):
        '''label must be less than 20 chars'''
        self.metadata[SigMFFile.ANNOTATION_KEY][0][SigMFFile.LABEL_KEY] = 'a' * 21
        with self.assertRaises(ValidationError):
            SigMFFile(self.metadata).validate()

    def test_invalid_type(self):
        '''license key must be string'''
        self.metadata[SigMFFile.GLOBAL_KEY][SigMFFile.LICENSE_KEY] = 1
        with self.assertRaises(ValidationError):
            SigMFFile(self.metadata).validate()

    def test_invalid_capture_order(self):
        '''metadata must have captures in order'''
        self.metadata[SigMFFile.CAPTURE_KEY] = [
            {SigMFFile.START_INDEX_KEY: 10},
            {SigMFFile.START_INDEX_KEY: 9}
        ]
        with self.assertRaises(ValidationError):
            SigMFFile(self.metadata).validate()

    def test_invalid_annotation_order(self):
        '''metadata must have annotations in order'''
        self.metadata[SigMFFile.ANNOTATION_KEY] = [
            {
                SigMFFile.START_INDEX_KEY: 2,
                SigMFFile.LENGTH_INDEX_KEY: 120000,
            },
            {
                SigMFFile.START_INDEX_KEY: 1,
                SigMFFile.LENGTH_INDEX_KEY: 120000,
            }
        ]
        with self.assertRaises(ValidationError):
            SigMFFile(self.metadata).validate()

    def test_invalid_hash(self):
        _, temp_path = tempfile.mkstemp()
        TEST_FLOAT32_DATA.tofile(temp_path)
        self.metadata[SigMFFile.GLOBAL_KEY][SigMFFile.HASH_KEY] = 'derp'
        with self.assertRaises(sigmf.error.SigMFFileError):
            SigMFFile(metadata=self.metadata, data_file=temp_path)
