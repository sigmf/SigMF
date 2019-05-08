import codecs
import json
import tarfile
import tempfile
from os import path

import numpy as np
import pytest

from sigmf import error
from sigmf.archive import SIGMF_DATASET_EXT, SIGMF_METADATA_EXT

from .testdata import TEST_FLOAT32_DATA, TEST_METADATA


def create_test_archive(test_sigmffile, tmpfile):
    sigmf_archive = test_sigmffile.archive(fileobj=tmpfile)
    sigmf_tarfile = tarfile.open(sigmf_archive, mode="r", format=tarfile.PAX_FORMAT)
    return sigmf_tarfile


def test_without_data_file_throws_fileerror(test_sigmffile):
    test_sigmffile.data_file = None
    with tempfile.NamedTemporaryFile() as temp:
        with pytest.raises(error.SigMFFileError):
            test_sigmffile.archive(name=temp.name)


def test_invalid_md_throws_validationerror(test_sigmffile):
    del test_sigmffile._metadata["global"]["core:datatype"]  # required field
    with tempfile.NamedTemporaryFile() as temp:
        with pytest.raises(error.SigMFValidationError):
            test_sigmffile.archive(name=temp.name)


def test_name_wrong_extension_throws_fileerror(test_sigmffile):
    with tempfile.NamedTemporaryFile() as temp:
        with pytest.raises(error.SigMFFileError):
            test_sigmffile.archive(name=temp.name + ".zip")


def test_fileobj_extension_ignored(test_sigmffile):
    with tempfile.NamedTemporaryFile(suffix=".tar") as temp:
        test_sigmffile.archive(fileobj=temp)


def test_name_used_in_fileobj(test_sigmffile):
    with tempfile.NamedTemporaryFile() as temp:
        sigmf_archive = test_sigmffile.archive(name="testarchive", fileobj=temp)
        sigmf_tarfile = tarfile.open(sigmf_archive, mode="r")
        basedir, file1, file2 = sigmf_tarfile.getmembers()
        assert basedir.name == "testarchive"

        def filename(tarinfo):
            path_root, _ = path.splitext(tarinfo.name)
            return path.split(path_root)[-1]

        assert filename(file1) == "testarchive"
        assert filename(file2) == "testarchive"


def test_fileobj_not_closed(test_sigmffile):
    with tempfile.NamedTemporaryFile() as temp:
        test_sigmffile.archive(fileobj=temp)
        assert not temp.file.closed


def test_unwritable_fileobj_throws_fileerror(test_sigmffile):
    with tempfile.NamedTemporaryFile(mode="rb") as temp:
        with pytest.raises(error.SigMFFileError):
            test_sigmffile.archive(fileobj=temp)


def test_unwritable_name_throws_fileerror(test_sigmffile):
    # Cannot assume /root/ is unwritable (e.g. Docker environment)
    # so use invalid filename
    unwritable_file = '/bad_name/'
    with pytest.raises(error.SigMFFileError):
        test_sigmffile.archive(name=unwritable_file)


def test_tarfile_layout(test_sigmffile):
    with tempfile.NamedTemporaryFile() as temp:
        sigmf_tarfile = create_test_archive(test_sigmffile, temp)
        basedir, file1, file2 = sigmf_tarfile.getmembers()
        assert tarfile.TarInfo.isdir(basedir)
        assert tarfile.TarInfo.isfile(file1)
        assert tarfile.TarInfo.isfile(file2)


def test_tarfile_names_and_extensions(test_sigmffile):
    with tempfile.NamedTemporaryFile() as temp:
        sigmf_tarfile = create_test_archive(test_sigmffile, temp)
        basedir, file1, file2 = sigmf_tarfile.getmembers()
        archive_name = basedir.name
        assert archive_name == path.split(temp.name)[-1]
        file_extensions = {SIGMF_DATASET_EXT, SIGMF_METADATA_EXT}

        file1_name, file1_ext = path.splitext(file1.name)
        assert file1_ext in file_extensions
        assert path.split(file1_name)[-1] == archive_name

        file_extensions.remove(file1_ext)

        file2_name, file2_ext = path.splitext(file2.name)
        assert path.split(file2_name)[-1] == archive_name
        assert file2_ext in file_extensions


def test_tarfile_persmissions(test_sigmffile):
    with tempfile.NamedTemporaryFile() as temp:
        sigmf_tarfile = create_test_archive(test_sigmffile, temp)
        basedir, file1, file2 = sigmf_tarfile.getmembers()
        assert basedir.mode == 0o755
        assert file1.mode == 0o644
        assert file2.mode == 0o644


def test_contents(test_sigmffile):
    with tempfile.NamedTemporaryFile() as temp:
        sigmf_tarfile = create_test_archive(test_sigmffile, temp)
        basedir, file1, file2 = sigmf_tarfile.getmembers()
        if file1.name.endswith(SIGMF_METADATA_EXT):
            mdfile = file1
            datfile = file2
        else:
            mdfile = file2
            datfile = file1

        bytestream_reader = codecs.getreader("utf-8")  # bytes -> str
        mdfile_reader = bytestream_reader(sigmf_tarfile.extractfile(mdfile))
        assert json.load(mdfile_reader) == TEST_METADATA

        datfile_reader = sigmf_tarfile.extractfile(datfile)
        # calling `fileno` on `tarfile.ExFileObject` throws error (?), but
        # np.fromfile requires it, so we need this extra step
        data = np.frombuffer(datfile_reader.read(), dtype=np.float32)

        assert np.array_equal(data, TEST_FLOAT32_DATA)


def test_tarfile_type(test_sigmffile):
    with tempfile.NamedTemporaryFile() as temp:
        sigmf_tarfile = create_test_archive(test_sigmffile, temp)
        assert sigmf_tarfile.format == tarfile.PAX_FORMAT
