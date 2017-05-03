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
"""
Tests
"""

import sigmf

MD_VALID = """
{
    "global": {
        "core:datatype": "cf32",
        "core:offset": 0,
        "core:version": "1.0.0",
        "core:license": "CC0",
        "core:date": "foo",
        "core:url": "foo",
        "core:sha512": "69a014f8855058d25b30b1caf4f9d15bb7b38afa26e28b24a63545734e534a861d658eddae1dbc666b33ca1d18c1ca85722f1f2f010703a7dbbef08189a1d0e5"
    },

    "capture": [
        {
            "core:sample_start": 0,
            "core:sampling_rate": 10000000,
            "core:frequency": 950000000,
            "core:time": "2017-02-01T11:33:17,053240428+01:00",
            "uhd:gain": 34
        },
        {
            "core:sample_start": 100000,
            "core:frequency": 950000000,
            "uhd:gain": 54
        }
    ],
    "annotations": [
        {
            "core:sample_start": 100000,
            "core:sample_count": 120000,
            "core:comment": "Some textual comment about stuff happenning",
            "gsm:xxx": 111
        }
    ]
}
"""

MD_INVALID_SEQUENCE_CAP = """
{
    "global": {
        "core:datatype": "cf32",
    },

    "capture": [
        {
            "core:sample_start": 10
        },
        {
            "core:sample_start": 9
        }
    ],
    "annotations": [
        {
            "core:sample_start": 100000,
            "core:comment": "stuff"
        }
    ]
}
"""

MD_INVALID_SEQUENCE_ANN = """
{
    "global": {
        "core:datatype": "cf32",
    },

    "capture": [
        {
            "core:sample_start": 0
        }
    ],
    "annotations": [
        {
            "core:sample_start": 2,
            "core:comment": "stuff"
        },
        {
            "core:sample_start": 1,
            "core:comment": "stuff"
        }
    ]
}
"""

MD_EMPTY = """
{}
"""

def test_valid_data():
    assert sigmf.SigMFFile(MD_VALID).validate()

def test_invalid_capture_seq():
    assert not sigmf.SigMFFile(MD_INVALID_SEQUENCE_CAP).validate()
    assert not sigmf.SigMFFile(MD_INVALID_SEQUENCE_ANN).validate()

def test_assert_empty():
    pass

def test_default_constructor():
    sigmf.SigMFFile()
