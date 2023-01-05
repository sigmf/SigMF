# Copyright: Multiple Authors
#
# This file is part of SigMF. https://github.com/gnuradio/SigMF
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Create and extract SigMF archives."""

import os
import shutil
import tarfile
import tempfile

from .error import SigMFFileError


SIGMF_ARCHIVE_EXT = ".sigmf"
SIGMF_METADATA_EXT = ".sigmf-meta"
SIGMF_DATASET_EXT = ".sigmf-data"
SIGMF_COLLECTION_EXT = ".sigmf-collection"


class SigMFArchive():
    """Archive a SigMFFile.

    A `.sigmf` file must include both valid metadata and data.
    If `self.data_file` is not set or the requested output file
    is not writable, raise `SigMFFileError`.

    Parameters:

      sigmffile -- A SigMFFile object with valid metadata and data_file

      name      -- path to archive file to create. If file exists, overwrite.
                   If `name` doesn't end in .sigmf, it will be appended.
                   For example: if `name` == "/tmp/archive1", then the
                   following archive will be created:
                       /tmp/archive1.sigmf
                       - archive1/
                         - archive1.sigmf-meta
                         - archive1.sigmf-data

      fileobj   -- If `fileobj` is specified, it is used as an alternative to
                   a file object opened in binary mode for `name`. It is
                   supposed to be at position 0. `name` is not required, but
                   if specified will be used to determine the directory and
                   file names within the archive. `fileobj` won't be closed.
                   For example: if `name` == "archive1" and fileobj is given,
                   a tar archive will be written to fileobj with the
                   following structure:
                       - archive1/
                         - archive1.sigmf-meta
                         - archive1.sigmf-data
    """
    def __init__(self, sigmffile, name=None, fileobj=None):
        self.sigmffile = sigmffile
        self.name = name
        self.fileobj = fileobj

        self._check_input()

        archive_name = self._get_archive_name()
        sigmf_fileobj = self._get_output_fileobj()
        sigmf_archive = tarfile.TarFile(mode="w",
                                        fileobj=sigmf_fileobj,
                                        format=tarfile.PAX_FORMAT)
        tmpdir = tempfile.mkdtemp()
        sigmf_md_filename = archive_name + SIGMF_METADATA_EXT
        sigmf_md_path = os.path.join(tmpdir, sigmf_md_filename)
        sigmf_data_filename = archive_name + SIGMF_DATASET_EXT
        sigmf_data_path = os.path.join(tmpdir, sigmf_data_filename)

        with open(sigmf_md_path, "w") as mdfile:
            self.sigmffile.dump(mdfile, pretty=True)

        shutil.copy(self.sigmffile.data_file, sigmf_data_path)

        def chmod(tarinfo):
            if tarinfo.isdir():
                tarinfo.mode = 0o755  # dwrxw-rw-r
            else:
                tarinfo.mode = 0o644  # -wr-r--r--
            return tarinfo

        sigmf_archive.add(tmpdir, arcname=archive_name, filter=chmod)
        sigmf_archive.close()
        if not fileobj:
            sigmf_fileobj.close()

        shutil.rmtree(tmpdir)

        self.path = sigmf_archive.name

    def _check_input(self):
        self._ensure_name_has_correct_extension()
        self._ensure_data_file_set()
        self._validate_sigmffile_metadata()

    def _ensure_name_has_correct_extension(self):
        name = self.name
        if name is None:
            return

        has_extension = "." in name
        has_correct_extension = name.endswith(SIGMF_ARCHIVE_EXT)
        if has_extension and not has_correct_extension:
            apparent_ext = os.path.splitext(name)[-1]
            err = "extension {} != {}".format(apparent_ext, SIGMF_ARCHIVE_EXT)
            raise SigMFFileError(err)

        self.name = name if has_correct_extension else name + SIGMF_ARCHIVE_EXT

    def _ensure_data_file_set(self):
        if not self.sigmffile.data_file:
            err = "no data file - use `set_data_file`"
            raise SigMFFileError(err)

    def _validate_sigmffile_metadata(self):
        self.sigmffile.validate()

    def _get_archive_name(self):
        if self.fileobj and not self.name:
            pathname = self.fileobj.name
        else:
            pathname = self.name

        filename = os.path.split(pathname)[-1]
        archive_name, archive_ext = os.path.splitext(filename)
        return archive_name

    def _get_output_fileobj(self):
        try:
            fileobj = self._get_open_fileobj()
        except:
            if self.fileobj:
                err = "fileobj {!r} is not byte-writable".format(self.fileobj)
            else:
                err = "can't open {!r} for writing".format(self.name)

            raise SigMFFileError(err)

        return fileobj

    def _get_open_fileobj(self):
        if self.fileobj:
            fileobj = self.fileobj
            fileobj.write(bytes())  # force exception if not byte-writable
        else:
            fileobj = open(self.name, "wb")

        return fileobj
