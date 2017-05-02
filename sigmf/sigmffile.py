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
SigMF File Representation Object
"""

import json
from six import iteritems
from sigmf.utils import dict_merge, insert_sorted_dict_list
from sigmf import validate
from sigmf import schema

def get_default_metadata(schema):
    """
    Return a valid annotation object based on defaults.
    """
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
            'dict_list': lambda x: [x],
        }[cat_type](defaults)
    return {
        category: default_category_data(desc["type"], get_default_dict(desc["keys"]))
        for category, desc in iteritems(schema)
    }

class SigMFFile(object):
    """
    API to manipulate annotation files.

    Parameters:
    metadata    -- Metadata. Either a string, or a dictionary.
    data_file   -- Path to the corresponding data file (optional).
    global_info -- Dictionary containing global header info.
    """
    START_INDEX_KEY = "core:sample_start"
    LENGTH_INDEX_KEY = "core:sample_length"
    START_OFFSET_KEY = "core:offset"
    HASH_KEY = "core:sha512"
    VERSION_KEY = "core:version"
    FILENAME_KEY = "core:datapath"
    GLOBAL_KEY = "global"
    CAPTURE_KEY = "capture"
    ANNOTATION_KEY = "annotation"

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
        elif isinstance(metadata, dict):
            self._metadata = metadata
        else:
            self._metadata = json.loads(metadata)
        if global_info is not None:
            self.set_global_info(global_info)
        self.data_file = data_file
        if self.data_file is not None:
            self.set_global_field(self.FILENAME_KEY, self.data_file)

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
        print(schema_section)
        for k, v in iteritems(entries):
            validate.validate_key_throw(
                v, schema_section.get(key, {}), section, k
            )

    def get_schema(self):
        """
        Return a schema object valid for the current metadata
        """
        current_metadata_version = self.get_global_info().get(self.VERSION_KEY)
        if self.version != current_metadata_version or self.schema is None:
            self.version = current_metadata_version
            from sigmf import schema
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
        print( schema_section.get(key, {}))
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

    def add_annotation(self, start_index, length, metadata):
        """
        Insert annotation
        """
        assert start_index >= self._get_start_offset()
        assert length > 1
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
        from sigmf import sigmf_hash
        the_hash = sigmf_hash.calculate_sha512(self.data_file)
        return self.set_global_field(self.HASH_KEY, the_hash)

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
        Write out the file.

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
