# Copyright 2017 GNU Radio Foundation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import shutil
import tempfile

import numpy as np

from sigmf import sigmffile, utils
from sigmf.sigmffile import SigMFFile

from .testdata import TEST_FLOAT32_DATA, TEST_METADATA


def simulate_capture(sigmf_md, n, capture_len):
    start_index = capture_len * n

    capture_md = {"core:datetime": utils.get_sigmf_iso8601_datetime_now()}

    sigmf_md.add_capture(start_index=start_index, metadata=capture_md)

    annotation_md = {
        "core:latitude": 40.0 + 0.0001 * n,
        "core:longitude": -105.0 + 0.0001 * n,
    }

    sigmf_md.add_annotation(start_index=start_index,
                            length=capture_len,
                            metadata=annotation_md)


def test_default_constructor():
    SigMFFile()


def test_set_non_required_global_field():
    sigf = SigMFFile()
    sigf.set_global_field('this_is:not_in_the_schema', None)


def test_add_capture():
    sigf = SigMFFile()
    sigf.add_capture(start_index=0, metadata={})


def test_add_annotation():
    sigf = SigMFFile()
    sigf.add_capture(start_index=0)
    meta = {"latitude": 40.0, "longitude": -105.0}
    sigf.add_annotation(start_index=0, length=128, metadata=meta)


def test_fromarchive(test_sigmffile):
    tf = tempfile.mkstemp()[1]
    td = tempfile.mkdtemp()
    archive_path = test_sigmffile.archive(name=tf)
    result = sigmffile.fromarchive(archive_path=archive_path, dir=td)

    assert result._metadata == test_sigmffile._metadata == TEST_METADATA

    data = np.fromfile(result.data_file, dtype=np.float32)
    assert np.array_equal(data, TEST_FLOAT32_DATA)

    os.remove(tf)
    shutil.rmtree(td)


def test_add_multiple_captures_and_annotations():
    sigf = SigMFFile()
    for idx in range(3):
        simulate_capture(sigf, idx, 1024)

def test_ordered_metadata():
    '''check to make sure the metadata is sorted as expected'''
    sigf = SigMFFile()
    top_sort_order = ['global', 'captures', 'annotations']
    for kdx, key in enumerate(sigf.ordered_metadata()):
        assert kdx == top_sort_order.index(key)

