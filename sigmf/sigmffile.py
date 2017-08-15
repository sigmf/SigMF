# Copyright 2016 GNU Radio Foundation
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

import codecs
import json
import tarfile
import tempfile
from os import path
from six import iteritems

from . import __version__, schema, sigmf_hash, validate
from .archive import SigMFArchive, SIGMF_DATASET_EXT, SIGMF_METADATA_EXT
from .utils import dict_merge, insert_sorted_dict_list


class SigMFFile(object):
    """API to manipulate SigMF files.

    Parameters:

      metadata    -- Metadata. Either a string, or a dictionary.
      data_file   -- Path to the corresponding data file.
      global_info -- Dictionary containing global header info.

    """
    START_INDEX_KEY = "core:sample_start"
    LENGTH_INDEX_KEY = "core:sample_count"
    START_OFFSET_KEY = "core:offset"
    HASH_KEY = "core:sha512"
    VERSION_KEY = "core:version"
    GLOBAL_KEY = "global"
    CAPTURE_KEY = "captures"
    ANNOTATION_KEY = "annotations"

    def __init__(
            self,
            metadata=None,
            data_file=None,
            global_info=None,
    ):
        self.version = None
        self.schema = None
        if metadata is None:
            self._metadata = get_default_metadata(self.get_schema())
            if not self._metadata[self.GLOBAL_KEY][self.VERSION_KEY]:
                self._metadata[self.GLOBAL_KEY][self.VERSION_KEY] = __version__
        elif isinstance(metadata, dict):
            self._metadata = metadata
        else:
            self._metadata = json.loads(metadata)
        if global_info is not None:
            self.set_global_info(global_info)
        self.data_file = data_file
        if self.data_file:
            self.calculate_hash()

    def _get_start_offset(self):
        """
        Return the offset of the first sample.
        """
        return self.get_global_field(self.START_OFFSET_KEY, 0)

    def _validate_dict_in_section(self, entries, section_key):
        """
        Checks a dictionary for validity.
        Throws if not.
        """
        schema_section = self.get_schema()[section_key]
        for k, v in iteritems(entries):
            validate.validate_key_throw(
                v, schema_section.get(k, {}), schema_section, k
            )

    def get_schema(self):
        """
        Return a schema object valid for the current metadata
        """
        current_metadata_version = self.get_global_info().get(self.VERSION_KEY)
        if self.version != current_metadata_version or self.schema is None:
            self.version = current_metadata_version
            self.schema = schema.get_schema(self.version)
        assert isinstance(self.schema, dict)
        return self.schema

    def set_global_info(self, new_global):
        """
        Overwrite the global info with a new dictionary.
        """
        self._validate_dict_in_section(new_global, self.GLOBAL_KEY)
        self._metadata[self.GLOBAL_KEY] = new_global

    def get_global_info(self):
        """
        Returns a dictionary with all the global info.
        """
        try:
            return self._metadata.get(self.GLOBAL_KEY, {})
        except AttributeError:
            return {}

    def set_global_field(self, key, value):
        """
        Inserts a value into the global fields.

        Will throw a ValueError if the key/value pair is invalid.
        """
        schema_section = self.get_schema()[self.GLOBAL_KEY].get('keys', {})
        validate.validate_key_throw(
            value,
            schema_section.get(key, {}),
            self.GLOBAL_KEY,
            key
        )
        self._metadata[self.GLOBAL_KEY][key] = value
        return value

    def get_global_field(self, key, default=None):
        """
        Return a field from the global info, or default if the field is not set.
        """
        return self._metadata[self.GLOBAL_KEY].get(key, default)

    def add_capture(self, start_index, metadata=None):
        """
        Insert capture info for sample starting at start_index.
        If there is already capture info for this index, metadata will be merged
        with the existing metadata, overwriting keys if they were previously
        set.
        """
        assert start_index >= self._get_start_offset()
        metadata = metadata or {}
        self._validate_dict_in_section(metadata, self.CAPTURE_KEY)
        metadata[self.START_INDEX_KEY] = start_index
        self._metadata[self.CAPTURE_KEY] = insert_sorted_dict_list(
            self._metadata.get(self.CAPTURE_KEY, []),
            metadata,
            self.START_INDEX_KEY,
        )

    def get_capture_info(self, index):
        """
        Returns a dictionary containing all the capture information at sample
        'index'.
        """
        assert index >= self._get_start_offset()
        captures = self._metadata.get(self.CAPTURE_KEY, [])
        assert len(captures) > 0
        cap_info = captures[0]
        for capture in captures:
            if capture[self.START_INDEX_KEY] > index:
                break
            cap_info = dict_merge(cap_info, capture)
        return cap_info

    def add_annotation(self, start_index, length, metadata=None):
        """
        Insert annotation
        """
        assert start_index >= self._get_start_offset()
        assert length > 1
        metadata = metadata or {}
        metadata[self.START_INDEX_KEY] = start_index
        metadata[self.LENGTH_INDEX_KEY] = length
        self._validate_dict_in_section(metadata, self.ANNOTATION_KEY)
        self._metadata[self.ANNOTATION_KEY] = insert_sorted_dict_list(
            self._metadata.get(self.ANNOTATION_KEY, []),
            metadata,
            self.START_INDEX_KEY,
        )

    def get_annotations(self, index):
        """
        Returns a list of dictionaries.
        Every dictionary contains one annotation for the sample at 'index'.
        """
        return [
            x for x in self._metadata.get(self.ANNOTATION_KEY, [])
            if x[self.START_INDEX_KEY] <= index
            and x[self.START_INDEX_KEY] + x[self.LENGTH_INDEX_KEY] > index
        ]

    def calculate_hash(self):
        """
        Calculates the hash of the data file and adds it to the global section.
        Also returns a string representation of the hash.
        """
        the_hash = sigmf_hash.calculate_sha512(self.data_file)
        return self.set_global_field(self.HASH_KEY, the_hash)

    def set_data_file(self, data_file):
        """
        Set the datafile path and recalculate the hash. Return the hash string.
        """
        self.data_file = data_file
        return self.calculate_hash()

    def validate(self):
        """
        Return True if the metadata is valid.
        """
        schema_version = self.get_global_field(self.VERSION_KEY)
        return validate.validate(
            self._metadata,
            schema.get_schema(schema_version),
        )

    def dump(self, filep, pretty=False):
        """
        Write metadata to a file.

        Parameters:
        filep -- File pointer or something that json.dump() can handle
        pretty -- If true, output will be formatted extra nicely.
        """
        json.dump(
            self._metadata,
            filep,
            indent=4 if pretty else None,
            separators=(',', ': ') if pretty else None,
        )

    def dumps(self, pretty=False):
        """
        Return a string representation of the metadata file.

        Parameters:
        pretty -- If true, output will be formatted extra nicely.
        """
        return json.dumps(
            self._metadata,
            indent=4 if pretty else None,
            separators=(',', ': ') if pretty else None,
        )

    def archive(self, name=None, fileobj=None):
        """Dump contents to SigMF archive format.

        `name` and `fileobj` are passed to SigMFArchive and are defined there.

        """
        archive = SigMFArchive(self, name, fileobj)
        return archive.path


def get_default_metadata(schema):
    """Return the minimal metadata that will pass the validator."""
    def get_default_dict(keys_dict):
        " Return a dict with all default values from keys_dict "
        return {
            key: desc.get("default")
            for key, desc in iteritems(keys_dict)
            if "default" in desc
        }

    def default_category_data(cat_type, defaults):
        " Return a valid data type for a category "
        return {
            'dict': lambda x: x,
            'dict_list': lambda x: [x] if x else [],
        }[cat_type](defaults)

    return {
        category: default_category_data(desc["type"], get_default_dict(desc["keys"]))
        for category, desc in iteritems(schema)
    }


def fromarchive(archive_path, dir=None):
    """Extract an archive and return a SigMFFile.

    If `dir` is given, extract the archive to that directory. Otherwise,
    the archive will be extracted to a temporary directory. For example,
    `dir` == "." will extract the archive into the current working
    directory.

    """
    if not dir:
        dir = tempfile.mkdtemp()

    archive = tarfile.open(archive_path)
    members = archive.getmembers()

    try:
        archive.extractall(path=dir)

        data_file = None
        metadata = None

        for member in members:
            if member.name.endswith(SIGMF_DATASET_EXT):
                data_file = path.join(dir, member.name)
            elif member.name.endswith(SIGMF_METADATA_EXT):
                bytestream_reader = codecs.getreader("utf-8")  # bytes -> str
                mdfile_reader = bytestream_reader(archive.extractfile(member))
                metadata = json.load(mdfile_reader)
    finally:
        archive.close()

    return SigMFFile(metadata=metadata, data_file=data_file)
