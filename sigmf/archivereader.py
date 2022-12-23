# Copyright: Multiple Authors
#
# This file is part of SigMF. https://github.com/gnuradio/SigMF
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Access SigMF archives without extracting them."""

import os
import shutil
import tarfile
import tempfile

from . import __version__  #, schema, sigmf_hash, validate
from .sigmffile import SigMFFile
from .archive import SigMFArchive, SIGMF_DATASET_EXT, SIGMF_METADATA_EXT, SIGMF_ARCHIVE_EXT
from .utils import dict_merge
from .error import SigMFFileError, SigMFAccessError


class SigMFArchiveReader():
    """Access data within SigMF archive `tar` in-place without extracting.

    Parameters:

      name      -- path to archive file to access. If file does not exist,
                   or if `name` doesn't end in .sigmf, SigMFFileError is raised.
    """
    def __init__(self, name=None, skip_checksum=False, map_readonly=True, archive_buffer=None):
        self.name = name
        if self.name is not None:
            if not name.endswith(SIGMF_ARCHIVE_EXT):
                err = "archive extension != {}".format(SIGMF_ARCHIVE_EXT)
                raise error.SigMFFileError(err)

            tar_obj = tarfile.open(self.name)

        elif archive_buffer is not None:
            tar_obj = tarfile.open(fileobj=archive_buffer, mode='r:')

        else:
            raise ValueError('In sigmf.archivereader.__init__(), either `name` or `archive_buffer` must be not None')

        json_contents = None
        data_offset_size = None

        for memb in tar_obj.getmembers():
            if memb.isdir():  # memb.type == tarfile.DIRTYPE:
                # the directory structure will be reflected in the member name
                continue

            elif memb.isfile():  # memb.type == tarfile.REGTYPE:
                if memb.name.endswith(SIGMF_METADATA_EXT):
                    json_contents = memb.name
                    if data_offset_size is None:
                        # consider a warnings.warn() here; the datafile should be earlier in the
                        # archive than the metadata, so that updating it (like, adding an annotation)
                        # is fast.
                        pass
                    with tar_obj.extractfile(memb) as memb_fid:
                        json_contents = memb_fid.read()

                elif memb.name.endswith(SIGMF_DATASET_EXT):
                    data_offset_size = memb.offset_data, memb.size

                else:
                    print('A regular file', memb.name, 'was found but ignored in the archive')
            else:
                print('A member of type', memb.type, 'and name', memb.name, 'was found but not handled, just FYI.')

        if data_offset_size is None:
            raise error.SigMFFileError('No .sigmf-data file found in archive!')

        self.sigmffile = SigMFFile(metadata=json_contents)
        valid_md = self.sigmffile.validate()
        if not valid_md:
            print('Metadata in archive did not .validate()!')

        self.sigmffile.set_data_file(self.name, data_buffer=archive_buffer, skip_checksum=skip_checksum, offset=data_offset_size[0],
                                     size_bytes=data_offset_size[1], map_readonly=map_readonly)

        self.ndim = self.sigmffile.ndim
        self.shape = self.sigmffile.shape

        tar_obj.close()

    def __len__(self):
        return self.sigmffile.__len__()

    def __iter__(self):
        return self.sigmffile.__iter__()

    def __getitem__(self, sli):
        return self.sigmffile.__getitem__(sli)
