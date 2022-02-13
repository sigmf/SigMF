#!/usr/bin/env python3

import os, tempfile
from scipy.io import wavfile
import sigmf
from sigmf import SigMFFile, SigMFArchive
from sigmf.utils import get_data_type_str

def writeSigMFArchiveFromWave(input_wav_filename, archive_filename=None, start_datetime=None, author=None):
    samplerate, wav_data = wavfile.read(input_wav_filename)

    global_info = {
        SigMFFile.DATATYPE_KEY: get_data_type_str(wav_data),
        SigMFFile.SAMPLE_RATE_KEY: samplerate,
        SigMFFile.DESCRIPTION_KEY: 'Converted from ' + input_wav_filename + '.',
        SigMFFile.VERSION_KEY: sigmf.__version__,
        SigMFFile.NUM_CHANNELS_KEY: 1 if len(wav_data.shape) < 2 else wav_data.shape[1],
        SigMFFile.RECORDER_KEY: os.path.basename(__file__),
    }
    if author is None:
        try:
            import getpass
        except:
            pass
        else:
            author = getpass.getuser()
    if author is not None:
        global_info[SigMFFile.AUTHOR_KEY]: author

    if start_datetime is None:
        import datetime, pathlib
        fname = pathlib.Path(input_wav_filename)
        mtime = datetime.datetime.fromtimestamp(fname.stat().st_mtime)
        start_datetime = mtime.isoformat() + 'Z'

    capture_info = {SigMFFile.START_INDEX_KEY: 0}
    if start_datetime is not None:
        capture_info[SigMFFile.DATETIME_KEY] = start_datetime

    tmpdir = tempfile.mkdtemp()
    sigmf_data_filename = input_wav_filename + sigmf.archive.SIGMF_DATASET_EXT
    sigmf_data_path = os.path.join(tmpdir, sigmf_data_filename)
    wav_data.tofile(sigmf_data_path)

    meta = sigmf.SigMFFile(data_file=sigmf_data_path, global_info=global_info)
    meta.add_capture(0, metadata=capture_info)

    if archive_filename is None:
        archive_filename = os.path.basename(input_wav_filename) + sigmf.archive.SIGMF_ARCHIVE_EXT
    meta.tofile(archive_filename, toarchive=True)
    return os.path.abspath(archive_filename)

if __name__ == '__main__':
    import sys
    input_wav_filename = sys.argv[1]  # produces an understandable error if nothing was provided on command line
    out_fname = writeSigMFArchiveFromWave(input_wav_filename)
    print("Wrote", out_fname)
