# flake8: noqa

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


import numpy as np
from sigmf import __version__
from sigmf import SigMFFile

TEST_FLOAT32_DATA = np.arange(16, dtype=np.float32)

TEST_METADATA = {
    SigMFFile.ANNOTATION_KEY: [{SigMFFile.LENGTH_INDEX_KEY: 16, SigMFFile.START_INDEX_KEY: 0}],
    SigMFFile.CAPTURE_KEY: [{SigMFFile.START_INDEX_KEY: 0}],
    SigMFFile.GLOBAL_KEY: {
        SigMFFile.DATATYPE_KEY: 'rf32_le',
        SigMFFile.HASH_KEY: 'f4984219b318894fa7144519185d1ae81ea721c6113243a52b51e444512a39d74cf41a4cec3c5d000bd7277cc71232c04d7a946717497e18619bdbe94bfeadd6',
        SigMFFile.VERSION_KEY: __version__
    }
}
