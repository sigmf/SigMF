import codecs
import json
import tarfile
import tempfile
from os import path

import numpy as np
import pytest

from sigmf import error
from sigmf import SigMFFile, SigMFArchiveReader
from sigmf.archive import SIGMF_DATASET_EXT, SIGMF_METADATA_EXT

def test_access_data_without_untar(test_sigmffile):
    global_info = {
            "core:author": "Glen M",
            "core:datatype": "ri16_le",
            "core:license": "https://creativecommons.org/licenses/by-sa/4.0/",
            "core:num_channels": 2,
            "core:sample_rate": 48000,
            "core:version": "1.0.0"
        }
    capture_info = {
            "core:datetime": "2021-06-18T23:17:51.163959Z",
            "core:sample_start": 0
        }
    
    NUM_ROWS = 5

    for dt in "ri16_le", "ci16_le", "rf32_le", "rf64_le", "cf32_le", "cf64_le":
        global_info["core:datatype"] = dt
        for num_chan in 1,3:
            global_info["core:num_channels"] = num_chan
            base_filename = dt + '_' + str(num_chan)
            archive_filename = base_filename + '.sigmf'
    
            a = np.arange(NUM_ROWS * num_chan * (2 if 'c' in dt else 1))
            if 'i16' in dt:
                b = a.astype(np.int16)
            elif 'f32' in dt:
                b = a.astype(np.float32)
            elif 'f64' in dt:
                b = a.astype(np.float64)
            else:
                raise ValueError('whoops')
    
            test_sigmffile.data_file = None
            with tempfile.NamedTemporaryFile() as temp:
                b.tofile(temp.name)
                meta = SigMFFile(data_file=temp.name, global_info=global_info)
                meta.add_capture(0, metadata=capture_info)
                meta.tofile(archive_filename, toarchive=True)

                archi = SigMFArchiveReader(archive_filename, skip_checksum=True)
